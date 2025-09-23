const rabbitmq_templates: Record<string, object> = {
  direct: {
    message: {
      to: "user@example.com",
      job: "send_email",
    },
    exchange: "my_direct_exchange",
    priority: 5,
    queue_args: {
      "x-message-ttl": 5000,
      "x-dead-letter-exchange": "dlx",
    },
    routing_key: "task",
    exchange_type: "direct",
  },
  fanout: {
    message: {
      event: "user_signup",
    },
    exchange: "my_fanout_exchange",
    queue_args: {},
    routing_key: "",
    exchange_type: "fanout",
  },
  topic: {
    message: {
      order_id: 123,
    },
    exchange: "my_topic_exchange",
    priority: 5,
    queue_args: {
      "x-message-ttl": 5000,
      "x-dead-letter-exchange": "dlx",
    },
    routing_key: "order.created",
    exchange_type: "topic",
  },
};
export { rabbitmq_templates };
