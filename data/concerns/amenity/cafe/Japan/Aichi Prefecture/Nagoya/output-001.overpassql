[out:json][timeout:30];
area["name:en"="Aichi Prefecture"]->.outer;
area["name:en"="Nagoya"]->.inner;
(
  nwr["amenity"="cafe"](area.inner)(area.outer);
);
out geom;