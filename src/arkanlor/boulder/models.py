# -*- coding: utf-8 -*-
from django.db import models
from django.contrib.contenttypes.models import ContentType
from django.contrib.auth.models import User

class WorldMap(models.Model):
    name = models.CharField(max_length=100)

class WorldMapRegion(models.Model):
    owners = models.ManyToManyField(User, related_name='regions', null=True, blank=True)
    map = models.ForeignKey(WorldMap, related_name='regions')
    name = models.CharField(max_length=100)
    public = models.BooleanField(default=False)
    access_level = models.IntegerField(default=0)
    def packet_info(self):
        areas = [ area.packet_info() for area in self.areas.all() ]
        return {'name': self.name,
                'count': len(areas),
                'areas': areas,
                }
    def add_area(self, area):
        return WorldMapArea(region=self,
                     x1=area.get('x1'),
                     y1=area.get('y1'),
                     x2=area.get('x2'),
                     y2=area.get('y2'),
                     ).save()
    def clear_areas(self):
        if self.areas.count():
            self.areas.all().delete()

class WorldMapArea(models.Model):
    region = models.ForeignKey(WorldMapRegion, related_name='areas')
    x1 = models.IntegerField()
    y1 = models.IntegerField()
    x2 = models.IntegerField()
    y2 = models.IntegerField()
    def packet_info(self):
        return {'x1': self.x1,
                'y1': self.y1,
                'x2': self.x2,
                'y2': self.y2,
                }

class WorldObjectType(models.Model):
    name = models.CharField(max_length=200, null=True)
    default_graphic = models.IntegerField()

class WorldObject(models.Model):
    worldmap = models.ForeignKey(WorldMap, related_name='world_objects', blank=True, null=True)
    object_type = models.ForeignKey(WorldObjectType, null=True)
    content_type = models.ForeignKey(ContentType, editable=False, null=True,)
    name = models.CharField(max_length=200, null=True)
    x = models.IntegerField()
    y = models.IntegerField()
    z = models.IntegerField()
    dir = models.IntegerField(default=0)
    custom_graphic = models.IntegerField(default= -1)
    color = models.IntegerField(default=0)

    def save(self, *args, **kwargs):
        if(not self.content_type):
            self.content_type = ContentType.objects.get_for_model(self.__class__)
        return super(WorldObject, self).save(*args, **kwargs)

    def as_leaf(self):
        """
            gets this object as its leaf.
        """
        content_type = self.content_type
        if (not content_type):
            return self
        model = content_type.model_class()
        return model.objects.get(id=self.id)

    def get_graphic(self):
        if self.custom_graphic < 0:
            if self.object_type is not None:
                return self.object_type.default_graphic
            else:
                return 0x01
        return self.custom_graphic
    def set_graphic(self, value):
        self.custom_graphic = value
    graphic = property(get_graphic, set_graphic)

class Item(WorldObject):
    amount = models.IntegerField(default=1)
    height = models.IntegerField(default=0)

    def packet_info(self):
        return {'color': self.color,
                'dir': self.dir,
                'x': self.x,
                'y': self.y,
                'z': self.z,
                'graphic': self.graphic,
                'amount': self.amount,
                'amount2': self.amount,
                }

class ItemMulti(Item):
    """
        Multi Item. An item which has small pseudoitems attached.
        @todo: width, height
    """
    # todo: serialize this in a textfield
    attached_buffer = models.TextField(blank=True, null=True) # add json list.

    def get_graphic(self):
        return 0x2000

    def get_items(self):
        # return my items as list
        return [item.packet_info() for item in self.attached_items.all()]
    items = property(get_items)

    def add_item(self, x, y, z, graphic):
        ItemMultiAttachment(item_multi=self,
                      x_offset=x,
                      y_offset=y,
                      z_offset=z or 0,
                      graphic=graphic).save()

    def packet_info(self):
        return {'color': self.color,
                'dir': self.dir,
                'x': self.x,
                'y': self.y,
                'z': self.z,
                'graphic': self.graphic,
                'amount': self.amount,
                'amount2': self.amount,
                # multi data:
                'datatype': 0x02,
                }

class ItemMultiAttachment(models.Model):
    item_multi = models.ForeignKey(ItemMulti, related_name='attached_items')
    x_offset = models.IntegerField(default=0)
    y_offset = models.IntegerField(default=0)
    z_offset = models.IntegerField(default=0)
    graphic = models.IntegerField()

    def packet_info(self):
        return {
                'x': self.x_offset,
                'y': self.y_offset,
                'z': self.z_offset,
                'graphic': self.graphic,
                }

class Mobile(WorldObject):
    body = models.IntegerField()
    hp = models.IntegerField()
    maxhp = models.IntegerField()
    #
    str = models.IntegerField()
    dex = models.IntegerField()
    int = models.IntegerField()
    #
    stam = models.IntegerField()
    maxstam = models.IntegerField()
    #
    mana = models.IntegerField()
    maxmana = models.IntegerField()
    #
    ar = models.IntegerField()
    active = models.BooleanField(default=False)

class PlayerMobile(Mobile):
    owner = models.ForeignKey(User, blank=True, null=True)
    logged_in = models.BooleanField(default=False)

