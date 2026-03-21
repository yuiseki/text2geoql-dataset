[out:json][timeout:30];
area["name:en"="Seoul"]->.outer;
area["name:en"="Mapo-gu"]->.inner;
(
  nwr["amenity"~"clinic|doctor"](area.inner)(area.outer);
);
out geom;
