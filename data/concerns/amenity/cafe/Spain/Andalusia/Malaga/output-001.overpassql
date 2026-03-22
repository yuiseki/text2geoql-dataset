[out:json][timeout:30];
area["name:en"="Andalusia"]->.outer;
area["name:en"="Malaga"]->.inner;
(
  nwr["amenity"="cafe"](area.inner)(area.outer);
);
out geom;