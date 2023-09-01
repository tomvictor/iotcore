import iotcore


# Define a callback function that will be called from Rust thread
def my_callback(message):
    print(f"Received message: {message}")

# Register the callback function with Rust thread
iotcore.start_thread(my_callback)

# Run the Rust thread (in a separate process or thread)
# The Rust thread will send messages to the callback function
# which will be printed by this Python program