import logging
import rospy

# taken from https://gist.github.com/ablakey/4f57dca4ea75ed29c49ff00edf622b38

class ConnectPythonLoggingToROS(logging.Handler):

    level_map = {
        logging.DEBUG: rospy.logdebug,
        logging.INFO: rospy.loginfo,
        logging.WARNING: rospy.logwarn,
        logging.ERROR: rospy.logerr,
        logging.CRITICAL: rospy.logfatal
    }

    def emit(self, record):
        try:
            self.level_map[record.levelno]("%s: %s" % (record.name, record.msg))
        except KeyError:
            rospy.logerr("unknown log level %s LOG: %s: %s" % (record.levelno, record.name, record.msg))


def route_logger_to_ros(logger_name):
    '''Re-routes a Python logging.logger to the ROS logging infrastructure.
    Without using this, once `rospy.init_node()` has been called, any use of `logging` occurs silently.

    Example:
        rospy.init_node('my_node')
        route_logger_to_ros('my_custom_library')

        # In an imported library:
        logger = logging.getLogger('my_custom_library)
        logger.info('This message gets routed to ROS logging if a ROS node was initialized in this process.')
    '''
    logging.getLogger(logger_name).addHandler(ConnectPythonLoggingToROS())
