[out:json][timeout:30];
area["name:en"="Seoul"]->.outer;
area["name:en"="Jongno-gu"]->.inner;
(
  nwr["amenity"="university"](area.inner)(area.outer);
);
out geom;
