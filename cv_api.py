# PlacesCNN to predict the scene category, attribute, and class activation map in a single pass
# by Bolei Zhou, sep 2, 2017
import time
import torch
from torch.autograd import Variable as V
import torchvision.models as models
from torchvision import transforms as trn
from torch.nn import functional as F
import os
import numpy as np
#from scipy.misc import imresize
import cv2
from PIL import Image
import matplotlib.pyplot as plt

features_blobs = []


en2emEn = {'airfield': 'sn', 'airplane_cabin': 'aj', 'airport_terminal': 'sn', 'alcove': 'qt', 'alley': 'aj', 'amphitheater': 'kl', 'amusement_arcade': 'ja', 'amusement_park': 'kl', 'apartment_building/outdoor': 'aj', 'aquarium': 'aj', 'aqueduct': 'qt', 'arcade': 'qt', 'arch': 'qt', 'archaelogical_excavation': 'aj', 'archive': 'aj', 'arena/hockey': 'ja', 'arena/performance': 'ja', 'arena/rodeo': 'ja', 'army_base': 'ja', 'art_gallery': 'zy', 'art_school': 'aj', 'art_studio': 'aj', 'artists_loft': 'aj', 'assembly_line': 'xx', 'athletic_field/outdoor': 'ja', 'atrium/public': 'aj', 'attic': 'aj', 'auditorium': 'tm', 'auto_factory': 'qt', 'auto_showroom': 'qt', 'badlands': 'aj', 'bakery/shop': 'zy', 'balcony/exterior': 'qt', 'balcony/interior': 'qt', 'ball_pit': 'kl', 'ballroom': 'kl', 'bamboo_forest': 'aj', 'bank_vault': 'qt', 'banquet_hall': 'tm', 'bar': 'ja', 'barn': 'qt', 'barndoor': 'qt', 'baseball_field': 'ja', 'basement': 'aj', 'basketball_court/indoor': 'ja', 'bathroom': 'zy', 'bazaar/indoor': 'xx', 'bazaar/outdoor': 'xx', 'beach': 'kl', 'beach_house': 'kl', 'beauty_salon': 'kl', 'bedchamber': 'aj', 'bedroom': 'aj', 'beer_garden': 'kl', 'beer_hall': 'kl', 'berth': 'jm', 'biology_laboratory': 'qt', 'boardwalk': 'aj', 'boat_deck': 'ja', 'boathouse': 'qt', 'bookstore': 'aj', 'booth/indoor': 'xx', 'botanical_garden': 'aj', 'bow_window/indoor': 'sn', 'bowling_alley': 'ja', 'boxing_ring': 'ja', 'bridge': 'sn', 'building_facade': 'xx', 'bullring': 'ja', 'burial_chamber': 'aj', 'bus_interior': 'xx', 'bus_station/indoor': 'xx', 'butchers_shop': 'zy', 'butte': 'jm', 'cabin/outdoor': 'aj', 'cafeteria': 'zy', 'campsite': 'aj', 'campus': 'aj', 'canal/natural': 'qt', 'canal/urban': 'qt', 'candy_store': 'zy', 'canyon': 'aj', 'car_interior': 'aj', 'carrousel': 'tm', 'castle': 'qt', 'catacomb': 'aj', 'cemetery': 'aj', 'chalet': 'zy', 'chemistry_lab': 'qt', 'childs_room': 'kl', 'church/indoor': 'tm', 'church/outdoor': 'tm', 'classroom': 'aj', 'clean_room': 'qt', 'cliff': 'aj', 'closet': 'jm', 'clothing_store': 'kl', 'coast': 'aj', 'cockpit': 'jm', 'coffee_shop': 'zy', 'computer_room': 'xx', 'conference_center': 'xx', 'conference_room': 'xx', 'construction_site': 'xx', 'corn_field': 'aj', 'corral': 'xx', 'corridor': 'aj', 'cottage': 'aj', 'courthouse': 'qt', 'courtyard': 'aj', 'creek': 'aj', 'crevasse': 'qt', 'crosswalk': 'xx', 'dam': 'xx', 'delicatessen': 'zy', 'department_store': 'zy', 'desert/sand': 'qt', 'desert/vegetation': 'aj', 'desert_road': 'aj', 'diner/outdoor': 'zy', 'dining_hall': 'zy', 'dining_room': 'zy', 'discotheque': 'kl', 'doorway/outdoor': 'qt', 'dorm_room': 'aj', 'downtown': 'xx', 'dressing_room': 'aj', 'driveway': 'xx', 'drugstore': 'zy', 'elevator/door': 'jm', 'elevator_lobby': 'jm', 'elevator_shaft': 'jm', 'embassy': 'qt', 'engine_room': 'aj', 'entrance_hall': 'aj', 'escalator/indoor': 'xx', 'excavation': 'aj', 'fabric_store': 'zy', 'farm': 'zy', 'fastfood_restaurant': 'zy', 'field/cultivated': 'xx', 'field/wild': 'aj', 'field_road': 'aj', 'fire_escape': 'qt', 'fire_station': 'qt', 'fishpond': 'aj', 'flea_market/indoor': 'xx', 'florist_shop/indoor': 'tm', 'food_court': 'zy', 'football_field': 'ja', 'forest/broadleaf': 'jm', 'forest_path': 'aj', 'forest_road': 'aj', 'formal_garden': 'aj', 'fountain': 'tm', 'galley': 'ja', 'garage/indoor': 'qt', 'garage/outdoor': 'qt', 'gas_station': 'qt', 'gazebo/exterior': 'aj', 'general_store/indoor': 'zy', 'general_store/outdoor': 'zy', 'gift_shop': 'tm', 'glacier': 'jm', 'golf_course': 'ja', 'greenhouse/indoor': 'zy', 'greenhouse/outdoor': 'jm', 'grotto': 'aj', 'gymnasium/indoor': 'ja', 'hangar/indoor': 'ja', 'hangar/outdoor': 'ja', 'harbor': 'sn', 'hardware_store': 'qt', 'hayfield': 'aj', 'heliport': 'ja', 'highway': 'aj', 'home_office': 'ja', 'home_theater': 'zy', 'hospital': 'zy', 'hospital_room': 'zy', 'hot_spring': 'zy', 'hotel/outdoor': 'zy', 'hotel_room': 'zy', 'house': 'zy', 'hunting_lodge/outdoor': 'qt', 'ice_cream_parlor': 'zy', 'ice_floe': 'aj', 'ice_shelf': 'aj', 'ice_skating_rink/indoor': 'ja', 'ice_skating_rink/outdoor': 'ja', 'iceberg': 'aj', 'igloo': 'tm', 'industrial_area': 'xx', 'inn/outdoor': 'zy', 'islet': 'jm', 'jacuzzi/indoor': 'zy', 'jail_cell': 'jm', 'japanese_garden': 'tm', 'jewelry_shop': 'tm', 'junkyard': 'xx', 'kasbah': 'xx', 'kennel/outdoor': 'xx', 'kindergarden_classroom': 'aj', 'kitchen': 'zy', 'lagoon': 'aj', 'lake/natural': 'aj', 'landfill': 'xx', 'landing_deck': 'qt', 'laundromat': 'xx', 'lawn': 'aj', 'lecture_room': 'ja', 'legislative_chamber': 'ja', 'library/indoor': 'aj', 'library/outdoor': 'aj', 'lighthouse': 'jm', 'living_room': 'zy', 'loading_dock': 'sn', 'lobby': 'aj', 'lock_chamber': 'qt', 'locker_room': 'zy', 'mansion': 'xx', 'manufactured_home': 'xx', 'market/indoor': 'xx', 'market/outdoor': 'xx', 'marsh': 'sg', 'martial_arts_gym': 'ja', 'mausoleum': 'sg', 'medina': 'qt', 'mezzanine': 'qt', 'moat/water': 'aj', 'mosque/outdoor': 'aj', 'motel': 'zy', 'mountain': 'aj', 'mountain_path': 'aj', 'mountain_snowy': 'aj', 'movie_theater/indoor': 'tm', 'museum/indoor': 'zy', 'museum/outdoor': 'zy', 'music_studio': 'zy', 'natural_history_museum': 'aj', 'nursery': 'xx', 'nursing_home': 'zy', 'oast_house': 'xx', 'ocean': 'aj', 'office': 'xx', 'office_building': 'xx', 'office_cubicles': 'xx', 'oilrig': 'xx', 'operating_room': 'zy', 'orchard': 'zy', 'orchestra_pit': 'ja', 'pagoda': 'qt', 'palace': 'ja', 'pantry': 'zy', 'park': 'aj', 'parking_garage/indoor': 'aj', 'parking_garage/outdoor': 'aj', 'parking_lot': 'aj', 'pasture': 'aj', 'patio': 'aj', 'pavilion': 'aj', 'pet_shop': 'zy', 'pharmacy': 'zy', 'phone_booth': 'xx', 'physics_laboratory': 'jm', 'picnic_area': 'zy', 'pier': 'xx', 'pizzeria': 'zy', 'playground': 'ja', 'playroom': 'ja', 'plaza': 'xx', 'pond': 'aj', 'porch': 'aj', 'promenade': 'tm', 'pub/indoor': 'xx', 'racecourse': 'xx', 'raceway': 'xx', 'raft': 'qt', 'railroad_track': 'xx', 'rainforest': 'aj', 'reception': 'xx', 'recreation_room': 'xx', 'repair_shop': 'xx', 'residential_neighborhood': 'xx', 'restaurant': 'zy', 'restaurant_kitchen': 'zy', 'restaurant_patio': 'zy', 'rice_paddy': 'aj', 'river': 'aj', 'rock_arch': 'aj', 'roof_garden': 'aj', 'rope_bridge': 'qt', 'ruin': 'sg', 'runway': 'ja', 'sandbox': 'qt', 'sauna': 'zy', 'schoolhouse': 'aj', 'science_museum': 'aj', 'server_room': 'xx', 'shed': 'zy', 'shoe_shop': 'zy', 'shopfront': 'zy', 'shopping_mall/indoor': 'xx', 'shower': 'zy', 'ski_resort': 'kl', 'ski_slope': 'kl', 'sky': 'aj', 'skyscraper': 'xx', 'slum': 'xx', 'snowfield': 'aj', 'soccer_field': 'ja', 'stable': 'xx', 'stadium/baseball': 'ja', 'stadium/football': 'ja', 'stadium/soccer': 'ja', 'stage/indoor': 'ja', 'stage/outdoor': 'ja', 'staircase': 'aj', 'storage_room': 'qt', 'street': 'xx', 'subway_station/platform': 'xx', 'supermarket': 'zy', 'sushi_bar': 'zy', 'swamp': 'sg', 'swimming_hole': 'ja', 'swimming_pool/indoor': 'ja', 'swimming_pool/outdoor': 'ja', 'synagogue/outdoor': 'tm', 'television_room': 'ja', 'television_studio': 'ja', 'temple/asia': 'aj', 'throne_room': 'aj', 'ticket_booth': 'xx', 'topiary_garden': 'tm', 'tower': 'qt', 'toyshop': 'zy', 'train_interior': 'xx', 'train_station/platform': 'aj', 'tree_farm': 'aj', 'tree_house': 'zy', 'trench': 'qt', 'tundra': 'aj', 'underwater/ocean_deep': 'aj', 'utility_room': 'jm', 'valley': 'aj', 'vegetable_garden': 'zy', 'veterinarians_office': 'qt', 'viaduct': 'xx', 'village': 'aj', 'vineyard': 'zy', 'volcano': 'ja', 'volleyball_court/outdoor': 'ja', 'waiting_room': 'sn', 'water_park': 'xx', 'water_tower': 'qt', 'waterfall': 'aj', 'watering_hole': 'xx', 'wave': 'zy', 'wet_bar': 'zy', 'wheat_field': 'aj', 'wind_farm': 'xx', 'windmill': 'zy', 'yard': 'aj', 'youth_hostel': 'zy', 'zen_garden': 'zy'}

def load_labels():
    # prepare all the labels
    # scene category relevant
    file_name_category = 'categories_places365.txt'
    if not os.access(file_name_category, os.W_OK):
        synset_url = 'https://raw.githubusercontent.com/csailvision/places365/master/categories_places365.txt'
        os.system('wget ' + synset_url)
    classes = list()
    with open(file_name_category) as class_file:
        for line in class_file:
            classes.append(line.strip().split(' ')[0][3:])
    classes = tuple(classes)

    # indoor and outdoor relevant
    file_name_IO = 'IO_places365.txt'
    if not os.access(file_name_IO, os.W_OK):
        synset_url = 'https://raw.githubusercontent.com/csailvision/places365/master/IO_places365.txt'
        os.system('wget ' + synset_url)
    with open(file_name_IO) as f:
        lines = f.readlines()
        labels_IO = []
        for line in lines:
            items = line.rstrip().split()
            labels_IO.append(int(items[-1]) -1) # 0 is indoor, 1 is outdoor
    labels_IO = np.array(labels_IO)

    # scene attribute relevant
    file_name_attribute = 'labels_sunattribute.txt'
    if not os.access(file_name_attribute, os.W_OK):
        synset_url = 'https://raw.githubusercontent.com/csailvision/places365/master/labels_sunattribute.txt'
        os.system('wget ' + synset_url)
    with open(file_name_attribute) as f:
        lines = f.readlines()
        labels_attribute = [item.rstrip() for item in lines]
    file_name_W = 'W_sceneattribute_wideresnet18.npy'
    if not os.access(file_name_W, os.W_OK):
        synset_url = 'http://places2.csail.mit.edu/models_places365/W_sceneattribute_wideresnet18.npy'
        os.system('wget ' + synset_url)
    W_attribute = np.load(file_name_W)

    return classes, labels_IO, labels_attribute, W_attribute

def hook_feature(module, input, output):
    features_blobs.append(np.squeeze(output.data.cpu().numpy())) #把tensor转换成numpy的格式


def returnTF():
# load the image transformer
    tf = trn.Compose([
        trn.Resize((224,224)),
        trn.ToTensor(),
        trn.Normalize([0.485, 0.456, 0.406], [0.229, 0.224, 0.225])
    ])
    return tf


def load_model1(myModel):
    model = myModel
    model.eval()
    # hook the feature extractor
    features_names = ['layer4','avgpool'] # this is the last conv layer of the resnet
    for name in features_names:
        model._modules.get(name).register_forward_hook(hook_feature)
    return model

def recong(myModel,filepath):
    # load the labels
    classes, labels_IO, labels_attribute, W_attribute = load_labels()

    # load the model
    features_blobs = []
    myModel = myModel
    model = load_model1(myModel)
    # load the transformer
    tf = returnTF() # image transformer

    # get the softmax weight
    params = list(model.parameters())
    weight_softmax = params[-2].data.numpy()
    weight_softmax[weight_softmax<0] = 0

    # load the test image
    img = Image.open(filepath)
    img = img.convert("RGB")
    input_img = V(tf(img).unsqueeze(0))

    # forward pass
    logit = model.forward(input_img)
    h_x = F.softmax(logit, 1).data.squeeze()
    probs, idx = h_x.sort(0, True)
    idx = idx.numpy()
    
    if classes[idx[0]] not in en2emEn:
        rst = 'qt'
    else:
        rst = en2emEn[classes[idx[0]]]

    return classes[idx[0]]

#测试接口调用
if __name__ == '__main__':
    from cv_model import *
    print(recong(model,'test.png'))