#!/usr/bin/env python
# -*- coding: utf-8 -*-

try:
    from .config import Configuration
except (ValueError, ImportError) as e:
    raise Exception("You may need to run byteBuggy from the root directory (which includes README.md)", e) from e


from .util.color import Color

import os
import subprocess


class ByteBuggy(object):

    def __init__(self):
        """
        Initializes byteBuggy.
        Checks that its running under *nix, with root permissions and ensures dependencies are installed.
        """

        self.print_banner()

        Configuration.initialize(load_interface=False)

        if os.name == 'nt':
            Color.pl('{!} {R}error: {O}byteBuggy{R} must be run under a {O}*NIX{W}{R} like OS')
            Configuration.exit_gracefully(0)
        if os.getuid() != 0:
            Color.pl('{!} {R}error: {O}byteBuggy{R} must be run as {O}root{W}')
            Color.pl('{!} {R}re-run with {O}sudo{W}')
            Configuration.exit_gracefully(0)

        from .tools.dependency import Dependency
        Dependency.run_dependency_check()

    def start(self):
        """
        Starts target-scan + attack loop, or launches utilities depending on user input.
        """
        from .model.result import CrackResult
        from .model.handshake import Handshake
        from .util.crack import CrackHelper

        if Configuration.show_cracked:
            CrackResult.display()

        elif Configuration.check_handshake:
            Handshake.check()

        elif Configuration.crack_handshake:
            CrackHelper.run()

        else:
            Configuration.get_monitor_mode_interface()
            self.scan_and_attack()

    @staticmethod
    def print_banner():
        print ('Origina Author: derv82')
        print('Original Repository: https://github.com/derv82/wifite2.git')
        print('''
                ___.            __        __________                           
\_ |__ ___.__._/  |_  ____\______   \__ __  ____   ____ ___.__.
 | __ <   |  |\   __\/ __ \|    |  _/  |  \/ ___\ / ___<   |  |
 | \_\ \___  | |  | \  ___/|    |   \  |  / /_/  > /_/  >___  |
 |___  / ____| |__|  \___  >______  /____/\___  /\___  // ____|
     \/\/                \/       \/     /_____//_____/ \/     
        
              ''')

    @staticmethod
    def scan_and_attack():
        """
        1) Scans for targets, asks user to select targets
        2) Attacks each target
        """
        from .util.scanner import Scanner
        from .attack.all import AttackAll

        Color.pl('')

        # Scan
        s = Scanner()
        do_continue = s.find_targets()
        targets = s.select_targets()

        if Configuration.infinite_mode:
            while do_continue:
                AttackAll.attack_multiple(targets)
                do_continue = s.update_targets()
                if not do_continue:
                    break
                targets = s.select_targets()
            attacked_targets = s.get_num_attacked()
        else:
            # Attack
            attacked_targets = AttackAll.attack_multiple(targets)

        Color.pl('{+} Finished attacking {C}%d{W} target(s), exiting' % attacked_targets)


def entry_point():
    try:
        byteBuggy = ByteBuggy()
        byteBuggy.start()
    except Exception as e:
        Color.pexception(e)
        Color.pl('\n{!} {R}Exiting{W}\n')

    except KeyboardInterrupt:
        Color.pl('\n{!} {O}Interrupted, Shutting down...{W}')

    # Delete Reaver .pcap
    subprocess.run(["rm", "reaver_output.pcap"], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    Configuration.exit_gracefully(0)


if __name__ == '__main__':
    entry_point()
