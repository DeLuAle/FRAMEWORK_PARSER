"""
Batch Conversion Script for TIA Portal XML to SCL Converter

Processes entire project directories, maintains folder structure in output,
validates conversions, and generates comprehensive error reports.

Usage:
    python batch_convert_project.py "PLC_410D1" --output "PLC_410D1_Parsed"
    python batch_convert_project.py "path/to/project"  # Output: path/to/project_Parsed
"""

import os
import sys
import argparse
import logging
import time
import csv
import traceback
from pathlib import Path
from datetime import datetime
from dataclasses import dataclass, field, asdict
from typing import Optional, List, Dict, Tuple
from collections import defaultdict

# Setup path to import local modules
current_dir = Path(__file__).parent
sys.path.insert(0, str(current_dir))

from main import identify_file_type, process_file
from utils import setup_logging

logger = logging.getLogger(__name__)


# ============================================================================
# DATA STRUCTURES
# ============================================================================

@dataclass
class FileResult:
    """Result of processing a single file"""
    source_path: Path
    relative_path: Path
    file_type: Optional[str]  # fb, fc, db, udt, tags, None
    status: str  # SUCCESS, FAILED, VALIDATION_ERROR, SKIPPED, IO_ERROR

    # Timing
    start_time: datetime = field(default_factory=datetime.now)
    processing_time: float = 0.0

    # Sizes
    input_size: int = 0
    output_size: Optional[int] = None

    # Output
    output_path: Optional[Path] = None

    # Error information
    error_type: Optional[str] = None  # PARSE_ERROR, VALIDATION_ERROR, IO_ERROR, etc.
    error_message: Optional[str] = None
    exception_trace: Optional[str] = None

    # Validation
    has_placeholders: bool = False
    placeholder_count: int = 0
    placeholder_lines: List[Tuple[int, str]] = field(default_factory=list)


@dataclass
class DirStats:
    """Statistics for a single directory"""
    path: Path
    total_files: int = 0
    success_count: int = 0
    failed_count: int = 0
    validation_error_count: int = 0
    skipped_count: int = 0

    @property
    def success_rate(self) -> float:
        processable = self.total_files - self.skipped_count
        return (self.success_count / processable * 100) if processable > 0 else 0.0


@dataclass
class BatchSummary:
    """Summary of batch processing results"""
    total_files: int = 0
    files_processed: int = 0
    files_succeeded: int = 0
    files_failed: int = 0
    files_validation_errors: int = 0
    files_skipped: int = 0

    file_type_counts: Dict[str, int] = field(default_factory=lambda: {'fb': 0, 'fc': 0, 'db': 0, 'udt': 0, 'tags': 0, 'scl_copy': 0})
    success_by_type: Dict[str, int] = field(default_factory=lambda: {'fb': 0, 'fc': 0, 'db': 0, 'udt': 0, 'tags': 0, 'scl_copy': 0})
    failed_by_type: Dict[str, int] = field(default_factory=lambda: {'fb': 0, 'fc': 0, 'db': 0, 'udt': 0, 'tags': 0, 'scl_copy': 0})
    validation_errors_by_type: Dict[str, int] = field(default_factory=lambda: {'fb': 0, 'fc': 0, 'db': 0, 'udt': 0, 'tags': 0, 'scl_copy': 0})

    total_time: float = 0.0
    total_input_size: int = 0
    total_output_size: int = 0

    processing_times: List[float] = field(default_factory=list)
    directory_stats: Dict[Path, DirStats] = field(default_factory=dict)

    @property
    def files_processable(self) -> int:
        return self.files_processed

    @property
    def success_rate(self) -> float:
        if self.files_processable == 0:
            return 0.0
        return (self.files_succeeded / self.files_processable * 100)

    @property
    def average_time(self) -> float:
        if len(self.processing_times) == 0:
            return 0.0
        return sum(self.processing_times) / len(self.processing_times)

    @property
    def min_time(self) -> float:
        return min(self.processing_times) if self.processing_times else 0.0

    @property
    def max_time(self) -> float:
        return max(self.processing_times) if self.processing_times else 0.0

    @property
    def median_time(self) -> float:
        if not self.processing_times:
            return 0.0
        sorted_times = sorted(self.processing_times)
        mid = len(sorted_times) // 2
        return sorted_times[mid] if len(sorted_times) % 2 != 0 else (sorted_times[mid-1] + sorted_times[mid]) / 2


# ============================================================================
# HELPER FUNCTIONS
# ============================================================================

def format_size(bytes_val: int) -> str:
    """Convert bytes to human-readable format"""
    for unit in ['B', 'KB', 'MB', 'GB', 'TB']:
        if bytes_val < 1024.0:
            return f"{bytes_val:.1f} {unit}"
        bytes_val /= 1024.0
    return f"{bytes_val:.1f} PB"


def format_duration(seconds: float) -> str:
    """Convert seconds to human-readable format"""
    if seconds < 60:
        return f"{seconds:.1f}s"
    elif seconds < 3600:
        mins = int(seconds // 60)
        secs = int(seconds % 60)
        return f"{mins}m {secs}s"
    else:
        hours = int(seconds // 3600)
        mins = int((seconds % 3600) // 60)
        return f"{hours}h {mins}m"


def calculate_eta(current: int, total: int, elapsed: float) -> str:
    """Calculate estimated time remaining"""
    if current == 0 or elapsed < 0.1:
        return "calculating..."

    rate = current / elapsed  # files per second
    remaining = total - current
    eta_seconds = remaining / rate

    return format_duration(eta_seconds)


def extract_placeholder_lines(content: str, max_lines: int = 10) -> List[Tuple[int, str]]:
    """Extract lines containing placeholder '???'"""
    lines = []
    for line_num, line in enumerate(content.split('\n'), 1):
        if '???' in line:
            lines.append((line_num, line.strip()))
            if len(lines) >= max_lines:
                break
    return lines


def find_output_file(output_dir: Path, stem: str, file_type: str) -> Optional[Path]:
    """Find output file generated based on type"""
    extensions = {
        'fb': '.scl',
        'fc': '.scl',
        'db': '.db',
        'udt': '.udt',
        'tags': '.csv',
        'scl_copy': '.scl'
    }

    ext = extensions.get(file_type)
    if not ext:
        return None

    # First try direct match
    output_file = output_dir / f"{stem}{ext}"
    if output_file.exists():
        return output_file

    # Try glob pattern (for cases where name differs from stem)
    try:
        matches = list(output_dir.glob(f"*{ext}"))
        if matches:
            # Return most recently created
            return max(matches, key=lambda p: p.stat().st_mtime)
    except:
        pass

    return None


def create_directory_mirror(source_root: Path, output_root: Path, xml_files: List[Path]) -> int:
    """Create mirrored directory structure"""
    dirs_created = 0
    dirs_to_create = set()

    # Collect all unique parent directories
    for xml_file in xml_files:
        rel_path = xml_file.relative_to(source_root)
        output_dir = output_root / rel_path.parent
        dirs_to_create.add(output_dir)

    # Create all directories
    for dir_path in sorted(dirs_to_create):
        try:
            dir_path.mkdir(parents=True, exist_ok=True)
            dirs_created += 1
        except Exception as e:
            logger.warning(f"Failed to create directory {dir_path}: {e}")

    return dirs_created


# ============================================================================
# FILE PROCESSOR
# ============================================================================

class FileProcessor:
    """Processes individual files with comprehensive tracking"""

    def process_with_tracking(self, xml_file: Path, output_dir: Path, source_root: Path) -> FileResult:
        """Process single file with error tracking and validation"""

        relative_path = xml_file.relative_to(source_root)
        result = FileResult(
            source_path=xml_file,
            relative_path=relative_path,
            file_type=None,
            status='SKIPPED',
            start_time=datetime.now()
        )

        # Step 1: Identify file type
        try:
            file_type = identify_file_type(xml_file)
            result.file_type = file_type

            if not file_type:
                result.status = 'SKIPPED'
                result.processing_time = 0.0
                return result

        except Exception as e:
            result.status = 'IO_ERROR'
            result.error_type = 'IO_ERROR'
            result.error_message = f"Error identifying file type: {str(e)}"
            result.processing_time = 0.0
            return result

        # Step 2: Record input size
        try:
            result.input_size = xml_file.stat().st_size
        except Exception as e:
            logger.warning(f"Could not get file size for {xml_file.name}: {e}")
            result.input_size = 0

        # Step 3: Process file
        start_time = time.time()

        try:
            # Ensure output directory exists
            output_dir.mkdir(parents=True, exist_ok=True)

            # Call existing process_file function (ZERO MODIFICATIONS)
            process_file(xml_file, output_dir)

        except FileNotFoundError as e:
            result.status = 'IO_ERROR'
            result.error_type = 'IO_ERROR'
            result.error_message = f"File not found: {str(e)}"
            result.processing_time = time.time() - start_time
            return result

        except PermissionError as e:
            result.status = 'IO_ERROR'
            result.error_type = 'IO_ERROR'
            result.error_message = f"Permission denied: {str(e)}"
            result.processing_time = time.time() - start_time
            return result

        except Exception as e:
            result.status = 'FAILED'
            result.error_type = 'PARSE_ERROR'
            result.error_message = f"Conversion failed: {str(e)}"
            result.exception_trace = traceback.format_exc()
            result.processing_time = time.time() - start_time
            return result

        result.processing_time = time.time() - start_time

        # Step 4: Find output file
        output_file = find_output_file(output_dir, xml_file.stem, file_type)

        if output_file and output_file.exists():
            result.output_path = output_file

            try:
                result.output_size = output_file.stat().st_size
            except:
                result.output_size = 0

            # Step 5: Validate output for placeholders
            validation_result = self.validate_output(output_file)
            result.has_placeholders = validation_result['has_placeholders']
            result.placeholder_count = validation_result['count']
            result.placeholder_lines = validation_result['lines']

            if validation_result['has_placeholders']:
                result.status = 'VALIDATION_ERROR'
                result.error_type = 'PLACEHOLDER_ERROR'
                result.error_message = f"Contains {validation_result['count']} '???' placeholder(s)"
            else:
                result.status = 'SUCCESS'
        else:
            result.status = 'FAILED'
            result.error_type = 'NO_OUTPUT'
            result.error_message = "No output file was generated"
            result.output_size = None

        return result

    def validate_output(self, output_file: Path) -> Dict:
        """Validate output file for quality issues"""
        try:
            with open(output_file, 'r', encoding='utf-8', errors='replace') as f:
                content = f.read()

            placeholder_count = content.count('???')
            placeholder_lines = extract_placeholder_lines(content) if placeholder_count > 0 else []

            return {
                'has_placeholders': placeholder_count > 0,
                'count': placeholder_count,
                'lines': placeholder_lines
            }

        except Exception as e:
            logger.warning(f"Error validating {output_file.name}: {e}")
            return {
                'has_placeholders': False,
                'count': 0,
                'lines': []
            }


# ============================================================================
# STATISTICS COLLECTOR
# ============================================================================

class StatisticsCollector:
    """Collects comprehensive statistics from batch processing"""

    def __init__(self):
        self.summary = BatchSummary()
        self.all_results = []

    def record_file(self, result: FileResult):
        """Update statistics from file result"""
        self.all_results.append(result)

        self.summary.total_files += 1

        if result.status == 'SKIPPED':
            self.summary.files_skipped += 1
        else:
            self.summary.files_processed += 1

            if result.processing_time > 0:
                self.summary.processing_times.append(result.processing_time)

            # Track by file type
            if result.file_type:
                self.summary.file_type_counts[result.file_type] += 1

                if result.status == 'SUCCESS':
                    self.summary.files_succeeded += 1
                    self.summary.success_by_type[result.file_type] += 1
                elif result.status == 'VALIDATION_ERROR':
                    self.summary.files_validation_errors += 1
                    self.summary.validation_errors_by_type[result.file_type] += 1
                elif result.status == 'FAILED' or result.status == 'IO_ERROR':
                    self.summary.files_failed += 1
                    self.summary.failed_by_type[result.file_type] += 1

            # Track input/output sizes
            if result.input_size > 0:
                self.summary.total_input_size += result.input_size
            if result.output_size and result.output_size > 0:
                self.summary.total_output_size += result.output_size

        # Update directory statistics
        dir_path = result.relative_path.parent
        if dir_path not in self.summary.directory_stats:
            self.summary.directory_stats[dir_path] = DirStats(path=dir_path)

        dir_stat = self.summary.directory_stats[dir_path]
        dir_stat.total_files += 1

        if result.status == 'SUCCESS':
            dir_stat.success_count += 1
        elif result.status == 'FAILED' or result.status == 'IO_ERROR':
            dir_stat.failed_count += 1
        elif result.status == 'VALIDATION_ERROR':
            dir_stat.validation_error_count += 1
        elif result.status == 'SKIPPED':
            dir_stat.skipped_count += 1

    def get_summary(self) -> BatchSummary:
        """Get final summary"""
        return self.summary


# ============================================================================
# ERROR FILE CREATOR
# ============================================================================

def create_error_file(output_dir: Path, result: FileResult):
    """Create .error placeholder file for failed conversions"""
    try:
        error_file_path = output_dir / f"{result.source_path.name}.error"

        content = f"""ERROR REPORT
============
File: {result.source_path.name}
Source Path: {result.source_path}
Relative Path: {result.relative_path}
Timestamp: {result.start_time.isoformat()}
Status: {result.status}

Error Type: {result.error_type or 'UNKNOWN'}
Error Message: {result.error_message or 'No message available'}
"""

        if result.exception_trace:
            content += f"""
Exception Details:
------------------
{result.exception_trace}
"""

        if result.has_placeholders and result.placeholder_lines:
            content += f"""
Placeholder Locations ({result.placeholder_count} found):
------------------
"""
            for line_num, line_text in result.placeholder_lines:
                content += f"Line {line_num}: {line_text}\n"

        content += f"""
Additional Information:
-----------------------
File Type: {result.file_type or 'unknown'}
Input Size: {format_size(result.input_size)}
Processing Time: {result.processing_time:.2f} seconds
"""

        if result.output_size is not None:
            content += f"Output Size: {format_size(result.output_size)}\n"

        if result.output_path:
            content += f"Output File: {result.output_path}\n"

        content += """
For more information, check the batch_conversion_report.csv file.
"""

        with open(error_file_path, 'w', encoding='utf-8') as f:
            f.write(content)

        logger.debug(f"Created error file: {error_file_path}")

    except Exception as e:
        logger.error(f"Failed to create error file: {e}")


# ============================================================================
# CSV REPORT GENERATOR
# ============================================================================

class CSVReportGenerator:
    """Generates comprehensive CSV report"""

    def generate(self, report_path: Path, source_root: Path, output_root: Path,
                 summary: BatchSummary, all_results: List[FileResult], total_time: float):
        """Generate CSV report"""
        try:
            with open(report_path, 'w', newline='', encoding='utf-8-sig') as f:
                writer = csv.writer(f, quoting=csv.QUOTE_MINIMAL)

                # Header
                writer.writerow(['BATCH CONVERSION REPORT'])
                writer.writerow(['Generated:', datetime.now().strftime('%Y-%m-%d %H:%M:%S')])
                writer.writerow(['Source:', str(source_root)])
                writer.writerow(['Output:', str(output_root)])
                writer.writerow([])

                # Summary section
                writer.writerow(['=== SUMMARY ==='])
                writer.writerow(['Total Files Discovered:', summary.total_files])
                writer.writerow(['Files Processed:', summary.files_processed])
                writer.writerow(['Successful Conversions:', summary.files_succeeded])
                writer.writerow(['Failed Conversions:', summary.files_failed])
                writer.writerow(['Validation Errors (??? found):', summary.files_validation_errors])
                writer.writerow(['Skipped (Non-XML/Unsupported):', summary.files_skipped])
                writer.writerow(['Overall Success Rate:', f"{summary.success_rate:.1f}%"])
                writer.writerow(['Total Processing Time:', format_duration(total_time)])
                writer.writerow(['Average Time per File:', f"{summary.average_time:.2f}s"])
                writer.writerow([])

                # File type distribution
                writer.writerow(['=== FILE TYPE DISTRIBUTION ==='])
                writer.writerow(['File Type', 'Total', 'Success', 'Failed', 'Validation Errors', 'Skipped', 'Success Rate'])

                for file_type in ['fb', 'fc', 'db', 'udt', 'tags']:
                    total = summary.file_type_counts.get(file_type, 0)
                    if total > 0:
                        success = summary.success_by_type.get(file_type, 0)
                        failed = summary.failed_by_type.get(file_type, 0)
                        validation = summary.validation_errors_by_type.get(file_type, 0)
                        skipped = total - success - failed - validation

                        # Calculate success rate (excluding skipped)
                        processable = total - skipped
                        if processable > 0:
                            rate = (success / processable * 100)
                        else:
                            rate = 0.0

                        writer.writerow([
                            file_type.upper(),
                            total,
                            success,
                            failed,
                            validation,
                            skipped,
                            f"{rate:.1f}%"
                        ])
                writer.writerow([])

                # Performance metrics
                writer.writerow(['=== PERFORMANCE METRICS ==='])
                writer.writerow(['Metric', 'Value'])
                writer.writerow(['Total Processing Time:', format_duration(total_time)])
                writer.writerow(['Average Time:', f"{summary.average_time:.2f}s"])
                writer.writerow(['Median Time:', f"{summary.median_time:.2f}s"])
                writer.writerow(['Min Time:', f"{summary.min_time:.2f}s"])
                writer.writerow(['Max Time:', f"{summary.max_time:.2f}s"])

                # Find slowest file
                if all_results:
                    slowest = max(all_results, key=lambda r: r.processing_time)
                    writer.writerow(['Slowest File:', f"{slowest.relative_path} ({slowest.processing_time:.2f}s)"])
                writer.writerow([])

                # File size analysis
                writer.writerow(['=== FILE SIZE ANALYSIS ==='])
                writer.writerow(['Metric', 'Value'])
                writer.writerow(['Total Input Size:', format_size(summary.total_input_size)])
                writer.writerow(['Total Output Size:', format_size(summary.total_output_size)])

                if summary.total_input_size > 0:
                    size_change = ((summary.total_output_size - summary.total_input_size) / summary.total_input_size * 100)
                    writer.writerow(['Size Change:', f"{size_change:+.1f}%"])

                if summary.files_processed > 0:
                    avg_input = summary.total_input_size / (summary.file_type_counts['fb'] + summary.file_type_counts['fc'] +
                                                             summary.file_type_counts['db'] + summary.file_type_counts['udt'])
                    avg_output = summary.total_output_size / (summary.files_succeeded + summary.files_validation_errors)
                    writer.writerow(['Average Input:', format_size(int(avg_input))])
                    writer.writerow(['Average Output:', format_size(int(avg_output))])

                writer.writerow([])

                # Directory breakdown
                writer.writerow(['=== DIRECTORY BREAKDOWN ==='])
                writer.writerow(['Directory', 'Total', 'Success', 'Failed', 'Validation Errors', 'Skipped', 'Success Rate'])

                for dir_path in sorted(summary.directory_stats.keys()):
                    dir_stat = summary.directory_stats[dir_path]
                    writer.writerow([
                        str(dir_path),
                        dir_stat.total_files,
                        dir_stat.success_count,
                        dir_stat.failed_count,
                        dir_stat.validation_error_count,
                        dir_stat.skipped_count,
                        f"{dir_stat.success_rate:.1f}%"
                    ])

                writer.writerow([])

                # Detailed results
                writer.writerow(['=== DETAILED FILE RESULTS ==='])
                writer.writerow([
                    'File Path', 'Relative Path', 'File Type', 'Status',
                    'Time (s)', 'Input Size (bytes)', 'Output Size (bytes)',
                    'Error Type', 'Error Message', 'Has Placeholders', 'Placeholder Count', 'Timestamp'
                ])

                for result in all_results:
                    writer.writerow([
                        str(result.source_path),
                        str(result.relative_path),
                        result.file_type or '',
                        result.status,
                        f"{result.processing_time:.2f}",
                        result.input_size,
                        result.output_size or '',
                        result.error_type or '',
                        result.error_message or '',
                        str(result.has_placeholders),
                        result.placeholder_count,
                        result.start_time.strftime('%Y-%m-%d %H:%M:%S')
                    ])

            logger.info(f"Report generated: {report_path}")

        except Exception as e:
            logger.error(f"Failed to generate CSV report: {e}")
            raise


# ============================================================================
# PROGRESS DISPLAY
# ============================================================================

class ProgressDisplay:
    """Display progress during batch processing"""

    def __init__(self, total: int):
        self.total = total
        self.start_time = time.time()
        self.success_count = 0
        self.failed_count = 0
        self.validation_error_count = 0
        self.skipped_count = 0

    def update(self, current: int, result: FileResult):
        """Update progress display"""
        # Update counters
        if result.status == 'SUCCESS':
            self.success_count += 1
            status_str = 'OK SUCCESS'
        elif result.status == 'FAILED' or result.status == 'IO_ERROR':
            self.failed_count += 1
            status_str = 'XX FAILED'
        elif result.status == 'VALIDATION_ERROR':
            self.validation_error_count += 1
            status_str = '!! VALIDATION_ERROR'
        elif result.status == 'SKIPPED':
            self.skipped_count += 1
            status_str = '-- SKIPPED'
        else:
            status_str = '?? UNKNOWN'

        # Display file info
        path_display = str(result.relative_path)
        if len(path_display) > 70:
            path_display = "..." + path_display[-67:]

        print(f"\n[{current}/{self.total}] {path_display}")

        if result.file_type:
            print(f"   Type: {result.file_type.upper()} | Size: {format_size(result.input_size)} | Status: {status_str} ({result.processing_time:.2f}s)")
        else:
            print(f"   Status: {status_str}")

        if result.status == 'VALIDATION_ERROR':
            print(f"   Warning: Contains {result.placeholder_count} '???' placeholder(s)")
        elif result.error_message:
            print(f"   Error: {result.error_message}")

        # Display progress bar
        elapsed = time.time() - self.start_time
        percentage = (current / self.total) * 100

        # Progress bar (30 chars) - ASCII safe for Windows console
        bar_length = 30
        filled = int(bar_length * current / self.total)
        bar = '=' * filled + '-' * (bar_length - filled)

        eta_str = calculate_eta(current, self.total, elapsed)

        print(f"\nProgress: {bar} {percentage:5.1f}% ({current}/{self.total})")
        print(f"Success: {self.success_count} | Failed: {self.failed_count} | Validation Errors: {self.validation_error_count} | Skipped: {self.skipped_count}")
        print(f"Rate: {(self.success_count/current*100):.1f}% | ETA: {eta_str}")


# ============================================================================
# MAIN
# ============================================================================

def print_header(source_root: Path, output_root: Path):
    """Print header"""
    print("\n" + "=" * 79)
    print("TIA Portal XML to SCL Batch Converter")
    print("=" * 79)
    print(f"Source:      {source_root}")
    print(f"Destination: {output_root}")
    print()


def print_final_summary(summary: BatchSummary, report_path: Path, total_time: float):
    """Print final summary"""
    print("\n" + "=" * 79)
    print("BATCH CONVERSION COMPLETE")
    print("=" * 79)
    print(f"Total Files:      {summary.total_files}")
    print(f"Processed:        {summary.files_processed}")
    print(f"Successful:       {summary.files_succeeded} ({summary.success_rate:.1f}%)")
    print(f"Failed:           {summary.files_failed} ({summary.files_failed/summary.total_files*100:.1f}%)")
    print(f"Validation Errors: {summary.files_validation_errors} ({summary.files_validation_errors/summary.total_files*100:.1f}%)")
    print(f"Skipped:          {summary.files_skipped} ({summary.files_skipped/summary.total_files*100:.1f}%)")
    print()
    print(f"Total Time:       {format_duration(total_time)}")
    print(f"Average Time:     {summary.average_time:.2f}s per file")
    print("=" * 79)
    print(f"\nReport saved to: {report_path}")
    print(f"Error files (.error) created in mirrored structure for failed/partial conversions")
    print()


def main():
    """Main entry point"""
    parser = argparse.ArgumentParser(
        description="Batch convert TIA Portal XML files to SCL with directory structure preservation"
    )
    parser.add_argument("source", nargs='?', default=os.getcwd(),
                       help="Source directory (default: current directory)")
    parser.add_argument("--output", "-o",
                       help="Output directory (default: {source}_Parsed)")

    args = parser.parse_args()

    source_root = Path(args.source).resolve()

    if not source_root.exists():
        print(f"ERROR: Source directory not found: {source_root}")
        sys.exit(1)

    if not source_root.is_dir():
        print(f"ERROR: Source is not a directory: {source_root}")
        sys.exit(1)

    # Determine output directory
    if args.output:
        output_root = Path(args.output).resolve()
    else:
        output_root = source_root.parent / f"{source_root.name}_Parsed"

    # Setup logging
    setup_logging()

    # Print header
    print_header(source_root, output_root)

    # Phase 1: Discover XML and SCL files
    print("Discovering XML and SCL files...")
    xml_files = sorted(source_root.rglob("*.xml"))
    scl_files = sorted(source_root.rglob("*.scl"))
    all_files = xml_files + scl_files

    if not all_files:
        print("No XML or SCL files found!")
        sys.exit(1)

    print(f"Found {len(xml_files)} XML files to convert")
    print(f"Found {len(scl_files)} SCL files to copy")
    print(f"Total: {len(all_files)} files")

    # Count unique directories
    unique_dirs = len(set(f.parent for f in all_files))
    max_depth = max(len(f.relative_to(source_root).parts) for f in all_files)
    print(f"Organized in {unique_dirs} directories (max depth: {max_depth} levels)")

    # Phase 2: Create mirrored directory structure
    print("\nCreating mirrored directory structure...")
    dirs_created = create_directory_mirror(source_root, output_root, all_files)
    print(f"Created {dirs_created} directories")

    # Phase 3: Initialize processors and collectors
    processor = FileProcessor()
    stats = StatisticsCollector()
    progress = ProgressDisplay(len(all_files))

    # Phase 4: Batch processing
    print("\nStarting batch conversion and copying...\n")
    batch_start_time = time.time()

    for i, source_file in enumerate(all_files, 1):
        # Calculate output directory
        relative_path = source_file.relative_to(source_root)
        output_dir = output_root / relative_path.parent

        # Process file with tracking
        result = processor.process_with_tracking(source_file, output_dir, source_root)

        # Record statistics
        stats.record_file(result)

        # Create error file if needed
        if result.status in ['FAILED', 'VALIDATION_ERROR', 'IO_ERROR']:
            create_error_file(output_dir, result)

        # Update progress
        progress.update(i, result)

    total_time = time.time() - batch_start_time
    summary = stats.get_summary()
    summary.total_time = total_time

    # Phase 5: Generate report
    print("\n\nGenerating report...")
    report_path = output_root / "batch_conversion_report.csv"

    report_generator = CSVReportGenerator()
    report_generator.generate(report_path, source_root, output_root, summary, stats.all_results, total_time)

    # Phase 6: Print final summary
    print_final_summary(summary, report_path, total_time)


if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        print("\n\nBatch conversion interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n\nERROR: {e}")
        traceback.print_exc()
        sys.exit(1)
