[out:json][timeout:30];
area["name:en"="Niigata Prefecture"]->.outer;
area["name:en"="Niigata"]->.inner;
(
  nwr["amenity"="cafe"](area.inner)(area.outer);
);
out geom;