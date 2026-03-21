[out:json][timeout:30];
area["name:en"="Seoul"]->.outer;
area["name:en"="Mapo-gu"]->.inner;
(
  nwr["amenity"="restaurant"]["cuisine"~"mexican"](area.inner)(area.outer);
);
out geom;
