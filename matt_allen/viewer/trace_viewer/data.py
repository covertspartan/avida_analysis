from __future__ import division

"""Simple class that allows you to access dictionary keys using
key or dot notation"""
class AttrDict(dict):
    def __getattr__(self, attr):
        return self[attr]
    def __setattr__(self, attr, value):
        self[attr] = value

"""Container for the data used by the viewer. This mainly exists
to keep the code separate"""
class Data(AttrDict):
    def __init__(self, *args):
        self.genome = []
        self.num_threads = 1
        self.total_steps = 0

        self.cycles = []
        self.micro_ops = []
        self.updates = []
        self.registers = []
        self.register_origins = []
        self.threads = []
        self.ips = []
        self.rhs = []
        self.whs = []
        self.fhs = []
        self.last_outputs = []
        self.merits = []
        self.bonuses = []
        self.forage_types = []
        self.group_i_ds = []
        self.cells = []
        self.avatar_cells = []
        self.directions = []
        self.occupieds = []
        self.hills = []
        self.walls = []
        self.instructions = []
        self.nops = []
        self.executeds = []
        self.queued_eats = []
        self.queued_moves = []
        self.queued_rots = []
        self.queued_rot_amounts = []

        self.resource_names = []
        self.resource_radius = []
        self.resource_positions = []


