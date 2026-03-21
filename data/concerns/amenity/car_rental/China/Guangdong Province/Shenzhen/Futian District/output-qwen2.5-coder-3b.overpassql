[out:json][timeout:30];
area["name:zh"="深圳市"]->.outer;
area["name:zh"="广东省"]->.inner;
(
  nwr["amenity"~"car_rental"](area.inner)(area.outer);
);
out geom;
