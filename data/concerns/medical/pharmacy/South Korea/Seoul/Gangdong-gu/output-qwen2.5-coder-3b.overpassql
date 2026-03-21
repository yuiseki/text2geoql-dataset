[out:json][timeout:30];
area["name:en"="Seoul"]->.outer;
area["name:en"="Gangdong-gu"]->.inner;
(
  nwr["amenity"="pharmacy"](area.inner)(area.outer);
);
out geom;
