[out:json][timeout:30];
area["name:en"="Seoul"]->.outer;
area["name:en"="Yangcheon-gu"]->.inner;
(
  nwr["amenity"="restaurant"]["cuisine"~"mexican"](area.inner)(area.outer);
);
out geom;
