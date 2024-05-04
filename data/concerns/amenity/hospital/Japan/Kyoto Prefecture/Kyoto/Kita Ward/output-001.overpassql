[out:json][timeout:30000];
area["name:en"="Kyoto"]->.outer;
area["name:en"="Kita Ward"]->.inner;
(
  nwr["amenity"="hospital"](area.inner)(area.outer);
);
out geom;
