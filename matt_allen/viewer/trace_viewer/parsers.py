from __future__ import division
import re


trace_parsers = {}

def parse_trace(key):
    """Decorate a function so that when it is defined it is registered as a trace parser.

    The key argument is used to identify the parser in settings.cfg.
    I.E., a function with the annotation '@parse_trace("name")' would be selected with
    the config line 'TRACE_TYPE name'

    When a new trace parser is added, use the @parse_trace(key) decoration before the def
    to apply the decorator and set up the settings support.
    """
    def decorator(func):
        def wrapper(*args, **kwargs):
            return func(*args, **kwargs)
        trace_parsers[key] = wrapper
        return wrapper
    return decorator

def parse_files(data, settings, callback):
    parse_data(data, settings, settings['genomefile'], 
                    lambda v, s, w: data.genome.append(w[0]))
    parse_data(data, settings, settings['tracefile'], 
                       trace_parsers[settings['tracetype']])
    parse_data(data, settings, settings['environmentfile'], parse_environment_line, 
                       delimiter=':')
    parse_data(data, settings, settings['resourcefile'], parse_resource_line)
    
    callback()
    

"""Read the Avida data file and parse each line with the line parser. 
A delimiter can be provided to separate the line into words for the line parser"""
def parse_data(data, settings, file, line_parser, delimiter=None):
    if delimiter is None:
        delimiter = ' '
    if file is not None:
        try:
            with open(file) as fp:
                for line in fp:
                    line = line.strip()
                    #parse only the characters before a '#' for comments
                    line = re.split('#', line)[0]
                    if len(line) > 0:
                        split = re.split(delimiter,line)
                        line_parser(data, settings, split)
        except IOError as e:
            print "I/O error({0}): {1} {2}".format(e.errno, e.strerror, file)


#parse one line of the trace file, assign the columns to appropriate variables
@parse_trace('bcr')
def parse_bcr_trace(data, settings, words):
    #catch the missing column at the end of the file
    if len(words) < 46:
        words.append('1')
    #only parse steps that executed
    if int(words[-1]) == 1:
        data.cycles.append(int(words[0]))
        data.micro_ops.append(int(words[1]))
        data.updates.append(int(words[2]))
        #parse registers
        regs = []
        reg_origins = []
        for i in xrange(0, settings['numregs']):
            regs.append(int(words[3 + 2 * i]))
            reg_origins.append(int(words[4 + 2 * i][1:-1]))
        data.registers.append(regs)
        data.register_origins.append(reg_origins)

        data.threads.append(int(words[27]))
        if data.threads[-1] + 1 > data.num_threads:
            data.num_threads = data.threads[-1] + 1

        data.ips.append(int(words[28]))
        data.rhs.append(int(words[29]))
        data.whs.append(int(words[30]))
        data.fhs.append(int(words[31]))
        data.last_outputs.append(int(words[32]))
        data.merits.append(int(words[33]))
        data.bonuses.append(int(words[34]))
        data.forage_types.append(int(words[35]))
        data.group_i_ds.append(int(words[36]))
        data.cells.append(int(words[37]))
        data.avatar_cells.append(int(words[38]))
        data.directions.append(int(words[39]))
        data.occupieds.append(int(words[40]))
        data.hills.append(int(words[41]))
        data.walls.append(int(words[42]))
        data.instructions.append(words[43])
        data.nops.append(words[44])
        data.executeds.append(int(words[45]))

        data.total_steps += 1

#parse one line of the trace file, assign the columns to appropriate variables
@parse_trace('gp8')
def parse_gp8_trace(data, settings, words):
    #catch the missing column at the end of the file
    if len(words) < 41:
        words.append('1')
    #only parse steps that executed
    if int(words[-1]) == 1:
        data.cycles.append(int(words[0]))
        data.micro_ops.append(int(words[1]))
        data.queued_eats.append(int(words[2]))
        data.queued_moves.append(int(words[3]))
        rot = re.search('(.*?)\((.*?)\)', words[4])
        data.queued_rots.append(int(rot.group(1)))
        data.queued_rot_amounts.append(int(rot.group(2)))
        data.updates.append(int(words[5]))
        #parse registers
        regs = []
        reg_origins = []
        num_regs = settings['numregs'];
        for i in xrange(num_regs):
            regs.append(int(words[6 + 2 * i]))
            reg_origins.append(int(words[7 + 2 * i][1:-1]))
        data.registers.append(regs)
        data.register_origins.append(reg_origins)

        data.threads.append(int(words[2 * num_regs + 6]))
        if data.threads[-1] + 1 > data.num_threads:
            data.num_threads = data.threads[-1] + 1

        data.ips.append(int(words[2 * num_regs + 7]))
        data.rhs.append(int(words[2 * num_regs + 8]))
        data.whs.append(int(words[2 * num_regs + 9]))
        data.fhs.append(int(words[2 * num_regs + 10]))
        data.last_outputs.append(int(words[2 * num_regs + 11]))
        data.merits.append(int(words[2 * num_regs + 12]))
        data.bonuses.append(int(words[2 * num_regs + 13]))
        data.forage_types.append(int(words[2 * num_regs + 14]))
        data.group_i_ds.append(int(words[2 * num_regs + 15]))
        data.cells.append(int(words[2 * num_regs + 16]))
        data.avatar_cells.append(int(words[2 * num_regs + 17]))
        data.directions.append(int(words[2 * num_regs + 18]))
        data.occupieds.append(int(words[2 * num_regs + 19]))
        data.hills.append(int(words[2 * num_regs + 20]))
        data.walls.append(int(words[2 * num_regs + 21]))
        data.instructions.append(words[2 * num_regs + 22])
        data.nops.append(words[2 * num_regs + 23])
        data.executeds.append(int(words[2 * num_regs + 24]))

        data.total_steps += 1

@parse_trace('analyze')
def parse_analyze_trace(data, settings, words):
    for word in words:
        split = re.split(':', word)
        if len(split) > 1:
            if 'IP' in split[0]:
                data.ips.append(int(split[1]))
                data.threads.append(0)
                data.updates.append(0)
                data.cycles.append(0)
                data.total_steps += 1
            elif 'AX' in split[0]:
                data.registers.append([int(split[1])])
            elif 'BX' in split[0]:
                data.registers[-1].append(int(split[1]))
            elif 'CX' in split[0]:
                data.registers[-1].append(int(split[1]))
            elif 'MeritBase' in split[0]:
                data.merits.append(int(split[1]))
            elif 'Bonus' in split[0]:
                data.bonuses.append(int(split[1]))
            elif 'EXECUTE' in split[0]:
                data.instructions.append(words[-1])
                data.nops.append('')


#parse one line of the resource file
def parse_resource_line(data, settings, words):
    for i, word in enumerate(words[1:]):
        cell = int(word)
        x = float(cell / settings['worldx'])
        y = float(cell % settings['worldx'])
        if len(data.resource_positions) <= i:
            data.resource_positions.append([(x,y)])
        else:
            data.resource_positions[i].append((x,y))

#parse one line of the environment file
def parse_environment_line(data, settings, words):
    #each word is a key and value, so split it up and put it in a dictionary for access
    settings = {}
    for word in words:
        split = re.split(' |=', word)
        if len(split) == 2:
            settings[split[0].strip()] = split[1].strip()

    #check if this line is a resource line
    name = settings.get('GRADIENT_RESOURCE')
    if name is not None:
        #if it is, get the available attributes
        data.resource_names.append(name)
        if 'spread' in settings:
            data.resource_radius.append(int(settings['spread']))
        else:
            data.resource_radius.append(None)


def parse_config_line(data, settings, words):
    name = words[0].replace('_', '').lower()
    if len(words) == 2:
        settings[name] = convert(words[1])
    else:
        settings[name] = [convert(word) for word in words[1:]]

def convert(word):
    """
    Parse a token from a file, converting to useful data.

    Tokens are converted to int or float if possible.
    """
    try:
        result= int(word)
    except ValueError:
        try:
            result = float(word)
        except ValueError:
            result = word

    return result