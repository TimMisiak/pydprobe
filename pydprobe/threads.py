import threading
import sys

def is_func_active(func):
    for tid, frame_info in sys._current_frames().items():
        cur_frame = frame_info
        while cur_frame:
            if cur_frame.f_code == func.__code__:
                return True
            cur_frame = cur_frame.f_back

def get_all_thread_frames():
    frames = []
    for thread in threading.enumerate():
        print(f"Thread ID: {thread.ident}, Name: {thread.name}")

        # Get the stack frames for this thread
        frames = sys._current_frames()
        thread_frame = frames.get(thread.ident)

        if thread_frame:
            # Walk through the stack frames of this thread
            while thread_frame:
                print(f"  File: {thread_frame.f_code.co_filename}, Line: {thread_frame.f_lineno}, Function: {thread_frame.f_code.co_name}")
                thread_frame = thread_frame.f_back