[out:json][timeout:30];
area["name:en"="Seoul"]->.outer;
area["name:en"="Gwanak-gu"]->.inner;
(
  nwr["amenity"~"clinic|doctor"](area.inner)(area.outer);
);
out geom;
