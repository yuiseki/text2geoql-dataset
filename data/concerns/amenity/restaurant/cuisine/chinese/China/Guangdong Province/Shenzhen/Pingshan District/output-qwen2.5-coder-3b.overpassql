[out:json][timeout:30];
area["name:zh"="深圳市"]->.outer;
area["name:zh"="坪山区"]->.inner;
(
  nwr["amenity"="restaurant"]["cuisine"~"chinese"](area.inner)(area.outer);
);
out geom;
