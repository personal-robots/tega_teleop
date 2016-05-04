# Jacqueline Kory Westlund
# May 2016
#
# The MIT License (MIT)
#
# Copyright (c) 2016 Personal Robots Group
# 
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
# 
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
# 
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.

from PySide import QtGui # basic GUI stuff
import rospy # ROS
from r1d1_msgs.msg import TegaAction # ROS msgs to talk to Tega
from r1d1_msgs.msg import TegaState # ROS msgs to get info from Tega
from sar_opal_msgs.msg import OpalCommand # ROS msgs to talk to tablet
from std_msgs.msg import Bool # for child_attention topic

class tega_teleop_ros():
    # ROS node
    # set up rostopics we publish: commands to the tablet and commands
    # to Tega
    tablet_pub = rospy.Publisher('opal_tablet_command', OpalCommand,
            queue_size = 10)
    tega_pub = rospy.Publisher('tega', TegaAction, queue_size = 10)

    def __init__(self, ros_node, ros_label, flags):
        """ Initialize ROS """
        # we get a reference to the main ros node so we can do callbacks
        # to publish messages, and subscribe to stuff
        self.ros_node = ros_node
        # we're going to update the ros label with info about messages coming
        # in one topics we're subscribed to
        self.ros_label = ros_label
        # these are shared flags that the UI code will use to change the colors
        # of text or buttons based on what messages we're getting
        self.flags = flags
        # subscribe to other ros nodes
        #TODO could we put list of nodes to subscribe to in config file?
        # the child attention topic gives us a boolean indicating whether or
        # not the affdex camera is recognizing a person's face looking in
        # generally the right direction
        rospy.Subscriber('child_attention', Bool, self.on_child_attn_msg)
        rospy.Subscriber('tega_state', TegaState, self.on_tega_state_msg)

    def send_opal_message(self, command):
        """ Publish opal command message """
        print 'sending opal command: %s' % command
        msg = OpalCommand()
        msg.command = command
        self.tablet_pub.publish(msg)
        rospy.loginfo(msg)

    def send_motion_message(self, motion):
        """ Publish TegaAction do motion message """
        print 'sending motion message: %s' % motion
        msg = TegaAction()
        msg.do_motion = True
        msg.motion = motion
        self.tega_pub.publish(msg)
        rospy.loginfo(msg)

    def send_lookat_message(self, lookat):
        """ Publish TegaAction lookat message """
        print 'sending lookat message: %s' % lookat
        msg = TegaAction()
        msg.do_look_at = True
        msg.look_at = lookat
        self.tega_pub.publish(msg)
        rospy.loginfo(msg)

    def send_speech_message(self, speech):
        """ Publish TegaAction playback audio message """
        print '\nsending speech message: %s' % speech
        msg = TegaAction()
        msg.do_sound_playback = True
        msg.wav_filename = speech
        self.tega_pub.publish(msg)
        rospy.loginfo(msg)

    def on_child_attn_msg(self, data):
        # when we get child attention messages, set a label to say whether the
        # child is attending or not, and also set a flag
        self.flags.child_is_attending = data.data
        if data.data:
            self.ros_label.setText("Child is ATTENDING")
        else:
            self.ros_label.setText("Child is NOT ATTENDING")

    def on_tega_state_msg(self, data):
        # when we get tega state messages, set a flag indicating whether the
        # robot is in motion or playing sound or not
        self.flags.tega_is_playing_sound = data.is_playing_sound
        
        # Instead of giving us a boolean to indicate whether tega is in motion
        # or not, we get the name of the animation. Let's check whether it is
        # our "idle" animation (usually, the idle animation is either
        # MOTION_IDLESTILL or MOTION_BREATHING).
        self.flags.tega_is_doing_motion = data.doing_motion
