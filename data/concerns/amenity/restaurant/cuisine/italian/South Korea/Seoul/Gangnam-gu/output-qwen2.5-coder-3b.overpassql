[out:json][timeout:30];
area["name:en"="Seoul"]->.outer;
area["name:en"="Gangnam-gu"]->.inner;
(
  nwr["amenity"="restaurant"]["cuisine"~"italian"](area.inner)(area.outer);
);
out geom;
