[out:json][timeout:30];
area["name:ja"="福岡市"]->.outer;
area["name:ja"="中央区"]->.inner;
(
  nwr["amenity"="restaurant"]["cuisine"~"indian"](area.inner)(area.outer);
);
out geom;
