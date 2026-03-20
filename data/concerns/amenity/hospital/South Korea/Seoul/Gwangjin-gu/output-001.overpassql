[out:json][timeout:30];
area["name:en"="Seoul"]->.outer;
area["name:en"="Gwangjin-gu"]->.inner;
(
  nwr["amenity"="hospital"](area.inner)(area.outer);
);
out geom;
