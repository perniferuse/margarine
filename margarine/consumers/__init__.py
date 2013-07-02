# Copyright (C) 2013 by Alex Brandt <alex.brandt@rackspace.com>
#
# margarine is freely distributable under the terms of an MIT-style license.
# See COPYING or http://www.opensource.org/licenses/mit-license.php.

from margarine.parameters import Parameters
from margarine.parameters import configure_logging

configure_logging()

from margarine.communication import get_channel
from margarine.consumers import users

def main():
    """Set us up the bomb.

    Create a consuming process for the various backend processes.

    """

    Parameters().parse()

    # TODO Manage threads for load balancing.

    channel = get_channel()

    users.register(channel)

    channel.start_consuming()

