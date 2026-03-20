[out:json][timeout:30];
area["name:en"="Kyoto Prefecture"]->.outer;
area["name:en"="Kyoto"]->.inner;
(
  nwr["amenity"="bar"](area.inner)(area.outer);
);
out geom;
