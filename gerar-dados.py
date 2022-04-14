#!/usr/bin/env python

import glob
import os
import sys

try:
    sys.path.append(glob.glob('../carla/dist/carla-*%d.%d-%s.egg' % (
        sys.version_info.major,
        sys.version_info.minor,
        'win-amd64' if os.name == 'nt' else 'linux-x86_64'))[0])
except IndexError:
    pass

import carla

import random
import time


SIMULATION_NAME = "Simulation_1"

FPS = 1000
FRAMES_SIMULADOS = 1000

def main():
    actor_list = []

    try:
        client = carla.Client('localhost', 2000)
        client.set_timeout(2.0)


        world = client.get_world()

        # Configura a simulação para ser executada de modo síncrono
        settings = world.get_settings()
        settings.synchronous_mode = True
        settings.fixed_delta_seconds = 1.0/FPS
        settings.no_rendering_mode = False
        world.apply_settings(settings)

        # The world contains the list blueprints that we can use for adding new
        # actors into the simulation.
        blueprint_library = world.get_blueprint_library()

        # Now let's filter all the blueprints of type 'vehicle' and choose one
        # at random.
        # bp = random.choice(blueprint_library.filter('vehicle'))
        bp = blueprint_library.filter('vehicle.citroen.c3')[0]
        print(bp)

        # Randomiza a cor do veículo
        if bp.has_attribute('color'):
            color = random.choice(bp.get_attribute('color').recommended_values)
            bp.set_attribute('color', color)

        # Escolhe a posição inicial do veículo
        transform = random.choice(world.get_map().get_spawn_points())

        # So let's tell the world to spawn the vehicle.
        vehicle = world.spawn_actor(bp, transform)

        # Cria veículo
        actor_list.append(vehicle)
        print('created %s' % vehicle.type_id)

        # Let's put the vehicle to drive around.
        vehicle.set_autopilot(True)

        # camera_bp = blueprint_library.find('sensor.camera.depth')
        # camera_transform = carla.Transform(carla.Location(x=1.5, z=2.4))
        # camera = world.spawn_actor(camera_bp, camera_transform, attach_to=vehicle)
        # actor_list.append(camera)
        # print('created %s' % camera.type_id)

        # # Now we register the function that will be called each time the sensor
        # # receives an image. In this example we are saving the image to disk
        # # converting the pixels to gray-scale.
        # cc = carla.ColorConverter.LogarithmicDepth
        # camera.listen(lambda image: image.save_to_disk('_out/%06d.png' % image.frame, cc))

        # Configura Lidar
        lidar_cam = None
        lidar_bp = world.get_blueprint_library().find('sensor.lidar.ray_cast')
        lidar_bp.set_attribute('channels',str(64))
        lidar_bp.set_attribute('points_per_second',str(1388889))  #  From reference 64/0.00004608
        lidar_bp.set_attribute('rotation_frequency',str(10))
        lidar_bp.set_attribute('upper_fov', str(2))
        lidar_bp.set_attribute('lower_fov', str(-24.8))
        lidar_bp.set_attribute('range',str(80))
        lidar_location = carla.Location(0,0,1.8)
        lidar_rotation = carla.Rotation(0,0,0)
        lidar_transform = carla.Transform(lidar_location,lidar_rotation)
        lidar_sen = world.spawn_actor(lidar_bp,lidar_transform,attach_to=vehicle)
        lidar_sen.listen(lambda point_cloud: point_cloud.save_to_disk(SIMULATION_NAME + '/lidar_output/%.6d.ply' % point_cloud.frame))

        # # Configura GNSS 1 - No Noise
        # gnss_bp = world.get_blueprint_library().find('sensor.other.gnss')
        # gnss_location = carla.Location(0,0,0)
        # gnss_rotation = carla.Rotation(0,0,0)
        # gnss_transform = carla.Transform(gnss_location,gnss_rotation)
        # gnss_bp.set_attribute("sensor_tick",str(3.0))
        # ego_gnss = world.spawn_actor(gnss_bp,gnss_transform,attach_to=ego_vehicle, attachment_type=carla.AttachmentType.Rigid)
        # def gnss_callback(gnss):
        #     print("GNSS measure:\n"+str(gnss)+'\n')
        # ego_gnss.listen(lambda gnss: gnss_callback(gnss))

        # # Configura GNSS 2 - Random Noise
        # gnss_bp = world.get_blueprint_library().find('sensor.other.gnss')
        # gnss_location = carla.Location(0,0,0)
        # gnss_rotation = carla.Rotation(0,0,0)
        # gnss_transform = carla.Transform(gnss_location,gnss_rotation)
        # gnss_bp.set_attribute("sensor_tick",str(3.0))
        # ego_gnss = world.spawn_actor(gnss_bp,gnss_transform,attach_to=ego_vehicle, attachment_type=carla.AttachmentType.Rigid)
        # def gnss_callback(gnss):
        #     print("GNSS measure:\n"+str(gnss)+'\n')
        # ego_gnss.listen(lambda gnss: gnss_callback(gnss))

        # # Configura GNSS 3 - Realistic Noise
        # gnss_bp = world.get_blueprint_library().find('sensor.other.gnss')
        # gnss_location = carla.Location(0,0,0)
        # gnss_rotation = carla.Rotation(0,0,0)
        # gnss_transform = carla.Transform(gnss_location,gnss_rotation)
        # gnss_bp.set_attribute("sensor_tick",str(3.0))
        # ego_gnss = world.spawn_actor(gnss_bp,gnss_transform,attach_to=ego_vehicle, attachment_type=carla.AttachmentType.Rigid)
        # def gnss_callback(gnss):
        #     print("GNSS measure:\n"+str(gnss)+'\n')
        # ego_gnss.listen(lambda gnss: gnss_callback(gnss))

        start_record = time.time()
        print("Inicio da coleta : ")
        frame_atual = 0
        while (frame_atual < FRAMES_SIMULADOS):
            frame_atual += 1
            if frame_atual % 100 == 0:
                print("Frame atual: " + str(frame_atual))
            world.tick()    # Pass to the next simulator frame
        
        print("Fim da colata : {}".format(time.time() - start_record))

        time.sleep(5)

    finally:

        print('destroying actors')
        # camera.destroy()
        lidar_sen.destroy()

        client.apply_batch([carla.command.DestroyActor(x) for x in actor_list])
        print('done.')


if __name__ == '__main__':

    main()
