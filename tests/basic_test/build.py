from cse6040_devkit.assignment import AssignmentBuilder
from solutions import *
from samplers import *
from demos import *
import logging

logger = logging.getLogger(__name__)
logging.basicConfig(filemode='w',
                    filename='build_log.txt', 
                    level=logging.INFO)

builder = AssignmentBuilder()

if __name__ == '__main__':

    builder.register_blueprint(sampler_bp)
    builder.register_blueprint(solutions_bp)
    builder.register_blueprint(demo_bp)
    builder.build()
    logger.debug(f"{builder.core=}")