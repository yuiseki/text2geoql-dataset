[out:json][timeout:30];
area["name:en"="Seoul"]->.outer;
area["name:en"="Gwangjin-gu"]->.inner;
(
  nwr["amenity"="casino"](area.inner)(area.outer);
);
out geom;
