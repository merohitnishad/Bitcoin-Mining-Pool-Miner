import hashlib
import multiprocessing
import time
from multiprocessing import Manager, Pool, Process
from src.helpers.logger import logger


def uint256_from_compact(c):
    """Converts a compact representation of a difficulty target into a full 256-bit integer."""
    nbytes = (c >> 24) & 0xFF
    v = (c & 0xFFFFFF) << (8 * (nbytes - 3))
    return v


def hash256(s):
    """Computes the double SHA-256 hash of the input data."""
    return hashlib.sha256(hashlib.sha256(s).digest()).digest()


def uint256_from_str(s):
    """Converts a 32-byte little-endian string into an integer."""
    return int.from_bytes(s[:32], "little")


def ser_uint256(u):
    """Serializes a 256-bit integer into a 32-byte little-endian representation."""
    return u.to_bytes(32, "little")


def calc_sha256(r, nNonce):
    """Calculates the SHA-256 hash for a given header and nonce."""
    r += nNonce.to_bytes(4, "little")
    sha256_val = uint256_from_str(hash256(r))
    return sha256_val


def precompute_header(version, prev_block, merkle_root, timestamp, bits_diff):
    """Precomputes the block header components that remain constant during mining."""
    r = b""
    r += version.to_bytes(4, "little", signed=True)
    r += ser_uint256(prev_block)
    r += ser_uint256(merkle_root)
    r += timestamp.to_bytes(4, "little")
    r += bits_diff.to_bytes(4, "little")
    return r


def proof_of_work(params):
    """Performs the proof-of-work by iterating over the nonce range and checking for a valid hash."""
    (
        version,
        prev_block,
        merkle_root,
        timestamp,
        bits_diff,
        start_nonce,
        end_nonce,
        target,
        base_header,
        found_nonce,
        progress_dict,
        process_index,
    ) = params

    logger.info(
        f"Process {multiprocessing.current_process().name} working on range {start_nonce} to {end_nonce}"
    )

    try:
        for nonce in range(start_nonce, end_nonce):
            if found_nonce.value is not None:
                return None  # Exit early if a valid nonce has been found

            hash_result = calc_sha256(base_header, nonce)
            progress_dict[process_index] = nonce  # Update progress

            if hash_result < target:
                found_nonce.value = nonce
                logger.info(
                    f"Valid nonce found by {multiprocessing.current_process().name}: Nonce={nonce}, Hash={hash_result}"
                )
                return nonce
    except Exception as e:
        logger.error(
            f"Error in process {multiprocessing.current_process().name}: {e}",
            exc_info=True,
        )

    return None


def display_progress(progress_dict, num_processes):
    """Periodically logs the progress of each process."""
    while True:
        time.sleep(10)
        try:
            progress = [progress_dict[i] for i in range(num_processes)]
            logger.info(f"Current progress: {progress}")
        except Exception as e:
            logger.error(f"Error reading progress: {e}", exc_info=True)
            break  # Exit the loop if we can no longer read the progress dict


def solve_block(
    version, prev_block, merkle_root, timestamp, bits_diff, start_nonce, end_nonce
):
    """Solves the block by distributing nonce ranges across multiple processes."""
    num_processes = max(
        multiprocessing.cpu_count() - 1, 1
    )  # Use one less than total CPU count, but at least 1
    target = uint256_from_compact(bits_diff)
    base_header = precompute_header(
        version, prev_block, merkle_root, timestamp, bits_diff
    )

    nonce_range = end_nonce - start_nonce
    range_per_process = nonce_range // num_processes

    logger.info(f"Using {num_processes} processes for mining.")

    pool = Pool(processes=num_processes)
    manager = Manager()
    found_nonce = manager.Value("i", None)  # Shared variable for the found nonce
    progress_dict = manager.dict({i: start_nonce for i in range(num_processes)})
    params = []

    for i in range(num_processes):
        sub_start_nonce = start_nonce + i * range_per_process
        sub_end_nonce = (
            start_nonce + (i + 1) * range_per_process
            if i != num_processes - 1
            else end_nonce
        )

        logger.info(
            f"Process {i} will work on range {sub_start_nonce} to {sub_end_nonce}"
        )
        params.append(
            (
                version,
                prev_block,
                merkle_root,
                timestamp,
                bits_diff,
                sub_start_nonce,
                sub_end_nonce,
                target,
                base_header,
                found_nonce,
                progress_dict,
                i,
            )
        )

    progress_display = Process(
        target=display_progress, args=(progress_dict, num_processes)
    )
    progress_display.start()

    try:
        results = pool.map(proof_of_work, params)
        for r in results:
            if r is not None:
                result = r
                break
    finally:
        logger.info("Terminating worker processes and stopping progress display.")
        pool.close()
        pool.terminate()
        progress_display.terminate()

    if found_nonce.value is None:
        logger.warning("Mining completed, but no valid nonce was found.")
        return "xxx"

    return found_nonce.value
