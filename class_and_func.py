# Define a class called 'Person'
class Person:
    def __init__(self, name, age):
        self.name = name
        self.age = age

    def introduce(self):
        print(f"Hello, my name is {self.name} and I am {self.age} years old.")

# Define a class called 'Book'
class Book:
    def __init__(self, title, author):
        self.title = title
        self.author = author

    def display_info(self):
        print(f"Title: {self.title}\nAuthor: {self.author}")

# Function outside the classes
def greet():
    print("Welcome to our Python program!")

# Function to create a library of books
def create_library():
    library = []
    book1 = Book("Python Programming", "John Smith")
    book2 = Book("Machine Learning Basics", "Alice Johnson")
    book3 = Book("Data Science for Beginners", "Bob Davis")
    library.extend([book1, book2, book3])
    return library

# Function to display the library of books
def display_library(library):
    for book in library:
        book.display_info()

# Function to introduce people
def introduce_people():
    person1 = Person("Alice", 25)
    person2 = Person("Bob", 30)
    person1.introduce()
    person2.introduce()

# Define a class for Products
class Product:
    def __init__(self, name, price, stock):
        self.name = name
        self.price = price
        self.stock = stock

    def display_info(self):
        print(f"Product: {self.name}\nPrice: ${self.price}\nStock: {self.stock} units")

# Define a class for Customers
class Customer:
    def __init__(self, name, email):
        self.name = name
        self.email = email
        self.cart = []

    def add_to_cart(self, product, quantity=1):
        if product.stock >= quantity:
            self.cart.append((product, quantity))
            product.stock -= quantity
            print(f"{quantity} {product.name}(s) added to your cart.")
        else:
            print(f"Sorry, not enough stock of {product.name} to add to your cart.")

    def view_cart(self):
        if not self.cart:
            print("Your cart is empty.")
        else:
            print("Your Shopping Cart:")
            total_price = 0
            for product, quantity in self.cart:
                print(f"{product.name} x{quantity}: ${product.price * quantity}")
                total_price += product.price * quantity
            print(f"Total: ${total_price}")

# Define a class for Orders
class Order:
    def __init__(self, customer, products):
        self.customer = customer
        self.products = products
        self.total_price = sum(product.price * quantity for product, quantity in products)

    def display_order(self):
        print(f"Order for {self.customer.name}:")
        for product, quantity in self.products:
            print(f"{product.name} x{quantity}: ${product.price * quantity}")
        print(f"Total: ${self.total_price}")

# Define a class for an Online Store
class OnlineStore:
    def __init__(self):
        self.products = [
            Product("Laptop", 800, 10),
            Product("Phone", 400, 20),
            Product("Tablet", 300, 15),
        ]
        self.customers = []

    def add_customer(self, name, email):
        customer = Customer(name, email)
        self.customers.append(customer)
        print(f"Customer {name} added to the store.")

    def find_customer(self, email):
        for customer in self.customers:
            if customer.email == email:
                return customer
        return None

    def process_order(self, customer, product_name, quantity=1):
        product = next((p for p in self.products if p.name == product_name), None)
        if product:
            customer.add_to_cart(product, quantity)
        else:
            print(f"Product {product_name} not found.")

    def display_store_info(self):
        print("Welcome to Our Online Store!")
        print("Available Products:")
        for product in self.products:
            product.display_info()

# Function to simulate an online shopping experience
def shop_online():
    store = OnlineStore()
    store.display_store_info()

    store.add_customer("Alice", "alice@example.com")
    store.add_customer("Bob", "bob@example.com")

    alice = store.find_customer("alice@example.com")
    bob = store.find_customer("bob@example.com")

    store.process_order(alice, "Laptop", 2)
    store.process_order(bob, "Phone")
    store.process_order(bob, "Camera")

    alice.view_cart()
    bob.view_cart()

    order1 = Order(alice, alice.cart)
    order2 = Order(bob, bob.cart)

    order1.display_order()
    order2.display_order()

# if __name__ == "__main__":
#     shop_online()

#----------

class PubSub:
    """
    PubSub provides publish, subscribe and listen support to Redis channels.

    After subscribing to one or more channels, the listen() method will block
    until a message arrives on one of the subscribed channels. That message
    will be returned and it's safe to start listening again.
    """

    PUBLISH_MESSAGE_TYPES = ("message", "pmessage", "smessage")
    UNSUBSCRIBE_MESSAGE_TYPES = ("unsubscribe", "punsubscribe", "sunsubscribe")
    HEALTH_CHECK_MESSAGE = "redis-py-health-check"

    def __init__(
        self,
        connection_pool,
        shard_hint=None,
        ignore_subscribe_messages: bool = False,
        encoder: Optional["Encoder"] = None,
        push_handler_func: Union[None, Callable[[str], None]] = None,
    ):
        self.connection_pool = connection_pool
        self.shard_hint = shard_hint
        self.ignore_subscribe_messages = ignore_subscribe_messages
        self.connection = None
        self.subscribed_event = threading.Event()
        # we need to know the encoding options for this connection in order
        # to lookup channel and pattern names for callback handlers.
        self.encoder = encoder
        self.push_handler_func = push_handler_func
        if self.encoder is None:
            self.encoder = self.connection_pool.get_encoder()
        self.health_check_response_b = self.encoder.encode(self.HEALTH_CHECK_MESSAGE)
        if self.encoder.decode_responses:
            self.health_check_response = ["pong", self.HEALTH_CHECK_MESSAGE]
        else:
            self.health_check_response = [b"pong", self.health_check_response_b]
        if self.push_handler_func is None:
            _set_info_logger()
        self.reset()

    def __enter__(self) -> "PubSub":
        return self

    def __exit__(self, exc_type, exc_value, traceback) -> None:
        self.reset()

    def __del__(self) -> None:
        try:
            # if this object went out of scope prior to shutting down
            # subscriptions, close the connection manually before
            # returning it to the connection pool
            self.reset()
        except Exception:
            pass

    def reset(self) -> None:
        if self.connection:
            self.connection.disconnect()
            self.connection._deregister_connect_callback(self.on_connect)
            self.connection_pool.release(self.connection)
            self.connection = None
        self.health_check_response_counter = 0
        self.channels = {}
        self.pending_unsubscribe_channels = set()
        self.shard_channels = {}
        self.pending_unsubscribe_shard_channels = set()
        self.patterns = {}
        self.pending_unsubscribe_patterns = set()
        self.subscribed_event.clear()

    def close(self) -> None:
        self.reset()

    def on_connect(self, connection) -> None:
        "Re-subscribe to any channels and patterns previously subscribed to"
        # NOTE: for python3, we can't pass bytestrings as keyword arguments
        # so we need to decode channel/pattern names back to unicode strings
        # before passing them to [p]subscribe.
        self.pending_unsubscribe_channels.clear()
        self.pending_unsubscribe_patterns.clear()
        self.pending_unsubscribe_shard_channels.clear()
        if self.channels:
            channels = {
                self.encoder.decode(k, force=True): v for k, v in self.channels.items()
            }
            self.subscribe(**channels)
        if self.patterns:
            patterns = {
                self.encoder.decode(k, force=True): v for k, v in self.patterns.items()
            }
            self.psubscribe(**patterns)
        if self.shard_channels:
            shard_channels = {
                self.encoder.decode(k, force=True): v
                for k, v in self.shard_channels.items()
            }
            self.ssubscribe(**shard_channels)

    @property
    def subscribed(self) -> bool:
        """Indicates if there are subscriptions to any channels or patterns"""
        return self.subscribed_event.is_set()

    def execute_command(self, *args):
        """Execute a publish/subscribe command"""

        # NOTE: don't parse the response in this function -- it could pull a
        # legitimate message off the stack if the connection is already
        # subscribed to one or more channels

        if self.connection is None:
            self.connection = self.connection_pool.get_connection(
                "pubsub", self.shard_hint
            )
            # register a callback that re-subscribes to any channels we
            # were listening to when we were disconnected
            self.connection._register_connect_callback(self.on_connect)
            if self.push_handler_func is not None and not HIREDIS_AVAILABLE:
                self.connection._parser.set_push_handler(self.push_handler_func)
        connection = self.connection
        kwargs = {"check_health": not self.subscribed}
        if not self.subscribed:
            self.clean_health_check_responses()
        self._execute(connection, connection.send_command, *args, **kwargs)

    def clean_health_check_responses(self) -> None:
        """
        If any health check responses are present, clean them
        """
        ttl = 10
        conn = self.connection
        while self.health_check_response_counter > 0 and ttl > 0:
            if self._execute(conn, conn.can_read, timeout=conn.socket_timeout):
                response = self._execute(conn, conn.read_response)
                if self.is_health_check_response(response):
                    self.health_check_response_counter -= 1
                else:
                    raise PubSubError(
                        "A non health check response was cleaned by "
                        "execute_command: {0}".format(response)
                    )
            ttl -= 1

    def _disconnect_raise_connect(self, conn, error) -> None:
        """
        Close the connection and raise an exception
        if retry_on_timeout is not set or the error
        is not a TimeoutError. Otherwise, try to reconnect
        """
        conn.disconnect()
        if not (conn.retry_on_timeout and isinstance(error, TimeoutError)):
            raise error
        conn.connect()

    def _execute(self, conn, command, *args, **kwargs):
        """
        Connect manually upon disconnection. If the Redis server is down,
        this will fail and raise a ConnectionError as desired.
        After reconnection, the ``on_connect`` callback should have been
        called by the # connection to resubscribe us to any channels and
        patterns we were previously listening to
        """
        return conn.retry.call_with_retry(
            lambda: command(*args, **kwargs),
            lambda error: self._disconnect_raise_connect(conn, error),
        )

    def parse_response(self, block=True, timeout=0):
        """Parse the response from a publish/subscribe command"""
        conn = self.connection
        if conn is None:
            raise RuntimeError(
                "pubsub connection not set: "
                "did you forget to call subscribe() or psubscribe()?"
            )

        self.check_health()

        def try_read():
            if not block:
                if not conn.can_read(timeout=timeout):
                    return None
            else:
                conn.connect()
            return conn.read_response(disconnect_on_error=False, push_request=True)

        response = self._execute(conn, try_read)

        if self.is_health_check_response(response):
            # ignore the health check message as user might not expect it
            self.health_check_response_counter -= 1
            return None
        return response

    def is_health_check_response(self, response) -> bool:
        """
        Check if the response is a health check response.
        If there are no subscriptions redis responds to PING command with a
        bulk response, instead of a multi-bulk with "pong" and the response.
        """
        return response in [
            self.health_check_response,  # If there was a subscription
            self.health_check_response_b,  # If there wasn't
        ]

    def check_health(self) -> None:
        conn = self.connection
        if conn is None:
            raise RuntimeError(
                "pubsub connection not set: "
                "did you forget to call subscribe() or psubscribe()?"
            )

        if conn.health_check_interval and time.time() > conn.next_health_check:
            conn.send_command("PING", self.HEALTH_CHECK_MESSAGE, check_health=False)
            self.health_check_response_counter += 1

    def _normalize_keys(self, data) -> Dict:
        """
        normalize channel/pattern names to be either bytes or strings
        based on whether responses are automatically decoded. this saves us
        from coercing the value for each message coming in.
        """
        encode = self.encoder.encode
        decode = self.encoder.decode
        return {decode(encode(k)): v for k, v in data.items()}

    def psubscribe(self, *args, **kwargs):
        """
        Subscribe to channel patterns. Patterns supplied as keyword arguments
        expect a pattern name as the key and a callable as the value. A
        pattern's callable will be invoked automatically when a message is
        received on that pattern rather than producing a message via
        ``listen()``.
        """
        if args:
            args = list_or_args(args[0], args[1:])
        new_patterns = dict.fromkeys(args)
        new_patterns.update(kwargs)
        ret_val = self.execute_command("PSUBSCRIBE", *new_patterns.keys())
        # update the patterns dict AFTER we send the command. we don't want to
        # subscribe twice to these patterns, once for the command and again
        # for the reconnection.
        new_patterns = self._normalize_keys(new_patterns)
        self.patterns.update(new_patterns)
        if not self.subscribed:
            # Set the subscribed_event flag to True
            self.subscribed_event.set()
            # Clear the health check counter
            self.health_check_response_counter = 0
        self.pending_unsubscribe_patterns.difference_update(new_patterns)
        return ret_val

    def punsubscribe(self, *args):
        """
        Unsubscribe from the supplied patterns. If empty, unsubscribe from
        all patterns.
        """
        if args:
            args = list_or_args(args[0], args[1:])
            patterns = self._normalize_keys(dict.fromkeys(args))
        else:
            patterns = self.patterns
        self.pending_unsubscribe_patterns.update(patterns)
        return self.execute_command("PUNSUBSCRIBE", *args)

    def subscribe(self, *args, **kwargs):
        """
        Subscribe to channels. Channels supplied as keyword arguments expect
        a channel name as the key and a callable as the value. A channel's
        callable will be invoked automatically when a message is received on
        that channel rather than producing a message via ``listen()`` or
        ``get_message()``.
        """
        if args:
            args = list_or_args(args[0], args[1:])
        new_channels = dict.fromkeys(args)
        new_channels.update(kwargs)
        ret_val = self.execute_command("SUBSCRIBE", *new_channels.keys())
        # update the channels dict AFTER we send the command. we don't want to
        # subscribe twice to these channels, once for the command and again
        # for the reconnection.
        new_channels = self._normalize_keys(new_channels)
        self.channels.update(new_channels)
        if not self.subscribed:
            # Set the subscribed_event flag to True
            self.subscribed_event.set()
            # Clear the health check counter
            self.health_check_response_counter = 0
        self.pending_unsubscribe_channels.difference_update(new_channels)
        return ret_val

    def unsubscribe(self, *args):
        """
        Unsubscribe from the supplied channels. If empty, unsubscribe from
        all channels
        """
        if args:
            args = list_or_args(args[0], args[1:])
            channels = self._normalize_keys(dict.fromkeys(args))
        else:
            channels = self.channels
        self.pending_unsubscribe_channels.update(channels)
        return self.execute_command("UNSUBSCRIBE", *args)

    def ssubscribe(self, *args, target_node=None, **kwargs):
        """
        Subscribes the client to the specified shard channels.
        Channels supplied as keyword arguments expect a channel name as the key
        and a callable as the value. A channel's callable will be invoked automatically
        when a message is received on that channel rather than producing a message via
        ``listen()`` or ``get_sharded_message()``.
        """
        if args:
            args = list_or_args(args[0], args[1:])
        new_s_channels = dict.fromkeys(args)
        new_s_channels.update(kwargs)
        ret_val = self.execute_command("SSUBSCRIBE", *new_s_channels.keys())
        # update the s_channels dict AFTER we send the command. we don't want to
        # subscribe twice to these channels, once for the command and again
        # for the reconnection.
        new_s_channels = self._normalize_keys(new_s_channels)
        self.shard_channels.update(new_s_channels)
        if not self.subscribed:
            # Set the subscribed_event flag to True
            self.subscribed_event.set()
            # Clear the health check counter
            self.health_check_response_counter = 0
        self.pending_unsubscribe_shard_channels.difference_update(new_s_channels)
        return ret_val

    def sunsubscribe(self, *args, target_node=None):
        """
        Unsubscribe from the supplied shard_channels. If empty, unsubscribe from
        all shard_channels
        """
        if args:
            args = list_or_args(args[0], args[1:])
            s_channels = self._normalize_keys(dict.fromkeys(args))
        else:
            s_channels = self.shard_channels
        self.pending_unsubscribe_shard_channels.update(s_channels)
        return self.execute_command("SUNSUBSCRIBE", *args)

    def listen(self):
        "Listen for messages on channels this client has been subscribed to"
        while self.subscribed:
            response = self.handle_message(self.parse_response(block=True))
            if response is not None:
                yield response

    def get_message(
        self, ignore_subscribe_messages: bool = False, timeout: float = 0.0
    ):
        """
        Get the next message if one is available, otherwise None.

        If timeout is specified, the system will wait for `timeout` seconds
        before returning. Timeout should be specified as a floating point
        number, or None, to wait indefinitely.
        """
        if not self.subscribed:
            # Wait for subscription
            start_time = time.time()
            if self.subscribed_event.wait(timeout) is True:
                # The connection was subscribed during the timeout time frame.
                # The timeout should be adjusted based on the time spent
                # waiting for the subscription
                time_spent = time.time() - start_time
                timeout = max(0.0, timeout - time_spent)
            else:
                # The connection isn't subscribed to any channels or patterns,
                # so no messages are available
                return None

        response = self.parse_response(block=(timeout is None), timeout=timeout)
        if response:
            return self.handle_message(response, ignore_subscribe_messages)
        return None

    get_sharded_message = get_message

    def ping(self, message: Union[str, None] = None) -> bool:
        """
        Ping the Redis server
        """
        args = ["PING", message] if message is not None else ["PING"]
        return self.execute_command(*args)

    def handle_message(self, response, ignore_subscribe_messages=False):
        """
        Parses a pub/sub message. If the channel or pattern was subscribed to
        with a message handler, the handler is invoked instead of a parsed
        message being returned.
        """
        if response is None:
            return None
        if isinstance(response, bytes):
            response = [b"pong", response] if response != b"PONG" else [b"pong", b""]
        message_type = str_if_bytes(response[0])
        if message_type == "pmessage":
            message = {
                "type": message_type,
                "pattern": response[1],
                "channel": response[2],
                "data": response[3],
            }
        elif message_type == "pong":
            message = {
                "type": message_type,
                "pattern": None,
                "channel": None,
                "data": response[1],
            }
        else:
            message = {
                "type": message_type,
                "pattern": None,
                "channel": response[1],
                "data": response[2],
            }

        # if this is an unsubscribe message, remove it from memory
        if message_type in self.UNSUBSCRIBE_MESSAGE_TYPES:
            if message_type == "punsubscribe":
                pattern = response[1]
                if pattern in self.pending_unsubscribe_patterns:
                    self.pending_unsubscribe_patterns.remove(pattern)
                    self.patterns.pop(pattern, None)
            elif message_type == "sunsubscribe":
                s_channel = response[1]
                if s_channel in self.pending_unsubscribe_shard_channels:
                    self.pending_unsubscribe_shard_channels.remove(s_channel)
                    self.shard_channels.pop(s_channel, None)
            else:
                channel = response[1]
                if channel in self.pending_unsubscribe_channels:
                    self.pending_unsubscribe_channels.remove(channel)
                    self.channels.pop(channel, None)
            if not self.channels and not self.patterns and not self.shard_channels:
                # There are no subscriptions anymore, set subscribed_event flag
                # to false
                self.subscribed_event.clear()

        if message_type in self.PUBLISH_MESSAGE_TYPES:
            # if there's a message handler, invoke it
            if message_type == "pmessage":
                handler = self.patterns.get(message["pattern"], None)
            elif message_type == "smessage":
                handler = self.shard_channels.get(message["channel"], None)
            else:
                handler = self.channels.get(message["channel"], None)
            if handler:
                handler(message)
                return None
        elif message_type != "pong":
            # this is a subscribe/unsubscribe message. ignore if we don't
            # want them
            if ignore_subscribe_messages or self.ignore_subscribe_messages:
                return None

        return message

    def run_in_thread(
        self,
        sleep_time: int = 0,
        daemon: bool = False,
        exception_handler: Optional[Callable] = None,
    ) -> "PubSubWorkerThread":
        for channel, handler in self.channels.items():
            if handler is None:
                raise PubSubError(f"Channel: '{channel}' has no handler registered")
        for pattern, handler in self.patterns.items():
            if handler is None:
                raise PubSubError(f"Pattern: '{pattern}' has no handler registered")
        for s_channel, handler in self.shard_channels.items():
            if handler is None:
                raise PubSubError(
                    f"Shard Channel: '{s_channel}' has no handler registered"
                )

        thread = PubSubWorkerThread(
            self, sleep_time, daemon=daemon, exception_handler=exception_handler
        )
        thread.start()
        return thread


class PubSubWorkerThread(threading.Thread):
    def __init__(
        self,
        pubsub,
        sleep_time: float,
        daemon: bool = False,
        exception_handler: Union[
            Callable[[Exception, "PubSub", "PubSubWorkerThread"], None], None
        ] = None,
    ):
        super().__init__()
        self.daemon = daemon
        self.pubsub = pubsub
        self.sleep_time = sleep_time
        self.exception_handler = exception_handler
        self._running = threading.Event()

    def run(self) -> None:
        if self._running.is_set():
            return
        self._running.set()
        pubsub = self.pubsub
        sleep_time = self.sleep_time
        while self._running.is_set():
            try:
                pubsub.get_message(ignore_subscribe_messages=True, timeout=sleep_time)
            except BaseException as e:
                if self.exception_handler is None:
                    raise
                self.exception_handler(e, pubsub, self)
        pubsub.close()

    def stop(self) -> None:
        # trip the flag so the run loop exits. the run loop will
        # close the pubsub connection, which disconnects the socket
        # and returns the connection to the pool.
        self._running.clear()


class Pipeline(Redis):
    """
    Pipelines provide a way to transmit multiple commands to the Redis server
    in one transmission.  This is convenient for batch processing, such as
    saving all the values in a list to Redis.

    All commands executed within a pipeline are wrapped with MULTI and EXEC
    calls. This guarantees all commands executed in the pipeline will be
    executed atomically.

    Any command raising an exception does *not* halt the execution of
    subsequent commands in the pipeline. Instead, the exception is caught
    and its instance is placed into the response list returned by execute().
    Code iterating over the response list should be able to deal with an
    instance of an exception as a potential value. In general, these will be
    ResponseError exceptions, such as those raised when issuing a command
    on a key of a different datatype.
    """

    UNWATCH_COMMANDS = {"DISCARD", "EXEC", "UNWATCH"}

    def __init__(self, connection_pool, response_callbacks, transaction, shard_hint):
        self.connection_pool = connection_pool
        self.connection = None
        self.response_callbacks = response_callbacks
        self.transaction = transaction
        self.shard_hint = shard_hint

        self.watching = False
        self.reset()

    def __enter__(self) -> "Pipeline":
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        self.reset()

    def __del__(self):
        try:
            self.reset()
        except Exception:
            pass

    def __len__(self) -> int:
        return len(self.command_stack)

    def __bool__(self) -> bool:
        """Pipeline instances should always evaluate to True"""
        return True

    def reset(self) -> None:
        self.command_stack = []
        self.scripts = set()
        # make sure to reset the connection state in the event that we were
        # watching something
        if self.watching and self.connection:
            try:
                # call this manually since our unwatch or
                # immediate_execute_command methods can call reset()
                self.connection.send_command("UNWATCH")
                self.connection.read_response()
            except ConnectionError:
                # disconnect will also remove any previous WATCHes
                self.connection.disconnect()
        # clean up the other instance attributes
        self.watching = False
        self.explicit_transaction = False
        # we can safely return the connection to the pool here since we're
        # sure we're no longer WATCHing anything
        if self.connection:
            self.connection_pool.release(self.connection)
            self.connection = None

    def close(self) -> None:
        """Close the pipeline"""
        self.reset()

    def multi(self) -> None:
        """
        Start a transactional block of the pipeline after WATCH commands
        are issued. End the transactional block with `execute`.
        """
        if self.explicit_transaction:
            raise RedisError("Cannot issue nested calls to MULTI")
        if self.command_stack:
            raise RedisError(
                "Commands without an initial WATCH have already been issued"
            )
        self.explicit_transaction = True

    def execute_command(self, *args, **kwargs):
        if (self.watching or args[0] == "WATCH") and not self.explicit_transaction:
            return self.immediate_execute_command(*args, **kwargs)
        return self.pipeline_execute_command(*args, **kwargs)

    def _disconnect_reset_raise(self, conn, error) -> None:
        """
        Close the connection, reset watching state and
        raise an exception if we were watching,
        retry_on_timeout is not set,
        or the error is not a TimeoutError
        """
        conn.disconnect()
        # if we were already watching a variable, the watch is no longer
        # valid since this connection has died. raise a WatchError, which
        # indicates the user should retry this transaction.
        if self.watching:
            self.reset()
            raise WatchError(
                "A ConnectionError occurred on while watching one or more keys"
            )
        # if retry_on_timeout is not set, or the error is not
        # a TimeoutError, raise it
        if not (conn.retry_on_timeout and isinstance(error, TimeoutError)):
            self.reset()
            raise

    def immediate_execute_command(self, *args, **options):
        """
        Execute a command immediately, but don't auto-retry on a
        ConnectionError if we're already WATCHing a variable. Used when
        issuing WATCH or subsequent commands retrieving their values but before
        MULTI is called.
        """
        command_name = args[0]
        conn = self.connection
        # if this is the first call, we need a connection
        if not conn:
            conn = self.connection_pool.get_connection(command_name, self.shard_hint)
            self.connection = conn

        return conn.retry.call_with_retry(
            lambda: self._send_command_parse_response(
                conn, command_name, *args, **options
            ),
            lambda error: self._disconnect_reset_raise(conn, error),
        )

    def pipeline_execute_command(self, *args, **options) -> "Pipeline":
        """
        Stage a command to be executed when execute() is next called

        Returns the current Pipeline object back so commands can be
        chained together, such as:

        pipe = pipe.set('foo', 'bar').incr('baz').decr('bang')

        At some other point, you can then run: pipe.execute(),
        which will execute all commands queued in the pipe.
        """
        self.command_stack.append((args, options))
        return self

    def _execute_transaction(self, connection, commands, raise_on_error) -> List:
        cmds = chain([(("MULTI",), {})], commands, [(("EXEC",), {})])
        all_cmds = connection.pack_commands(
            [args for args, options in cmds if EMPTY_RESPONSE not in options]
        )
        connection.send_packed_command(all_cmds)
        errors = []

        # parse off the response for MULTI
        # NOTE: we need to handle ResponseErrors here and continue
        # so that we read all the additional command messages from
        # the socket
        try:
            self.parse_response(connection, "_")
        except ResponseError as e:
            errors.append((0, e))

        # and all the other commands
        for i, command in enumerate(commands):
            if EMPTY_RESPONSE in command[1]:
                errors.append((i, command[1][EMPTY_RESPONSE]))
            else:
                try:
                    self.parse_response(connection, "_")
                except ResponseError as e:
                    self.annotate_exception(e, i + 1, command[0])
                    errors.append((i, e))

        # parse the EXEC.
        try:
            response = self.parse_response(connection, "_")
        except ExecAbortError:
            if errors:
                raise errors[0][1]
            raise

        # EXEC clears any watched keys
        self.watching = False

        if response is None:
            raise WatchError("Watched variable changed.")

        # put any parse errors into the response
        for i, e in errors:
            response.insert(i, e)

        if len(response) != len(commands):
            self.connection.disconnect()
            raise ResponseError(
                "Wrong number of response items from pipeline execution"
            )

        # find any errors in the response and raise if necessary
        if raise_on_error:
            self.raise_first_error(commands, response)

        # We have to run response callbacks manually
        data = []
        for r, cmd in zip(response, commands):
            if not isinstance(r, Exception):
                args, options = cmd
                command_name = args[0]
                if command_name in self.response_callbacks:
                    r = self.response_callbacks[command_name](r, **options)
            data.append(r)
        return data

    def _execute_pipeline(self, connection, commands, raise_on_error):
        # build up all commands into a single request to increase network perf
        all_cmds = connection.pack_commands([args for args, _ in commands])
        connection.send_packed_command(all_cmds)

        response = []
        for args, options in commands:
            try:
                response.append(self.parse_response(connection, args[0], **options))
            except ResponseError as e:
                response.append(e)

        if raise_on_error:
            self.raise_first_error(commands, response)
        return response

    def raise_first_error(self, commands, response):
        for i, r in enumerate(response):
            if isinstance(r, ResponseError):
                self.annotate_exception(r, i + 1, commands[i][0])
                raise r

    def annotate_exception(self, exception, number, command):
        cmd = " ".join(map(safe_str, command))
        msg = (
            f"Command # {number} ({cmd}) of pipeline "
            f"caused error: {exception.args[0]}"
        )
        exception.args = (msg,) + exception.args[1:]

    def parse_response(self, connection, command_name, **options):
        result = Redis.parse_response(self, connection, command_name, **options)
        if command_name in self.UNWATCH_COMMANDS:
            self.watching = False
        elif command_name == "WATCH":
            self.watching = True
        return result

#----------
# Main function
def main():
    greet()
    library = create_library()
    print("\nLibrary of Books:")
    display_library(library)
    print("\nIntroducing People:")
    introduce_people()

if __name__ == "__main__":
    main()
