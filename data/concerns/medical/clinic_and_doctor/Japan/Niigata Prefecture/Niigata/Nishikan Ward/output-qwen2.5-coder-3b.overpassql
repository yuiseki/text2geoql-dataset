[out:json][timeout:30];
area["name:en"="Niigata"]->.outer;
area["name:en"="Niigata Prefecture"]->.inner;
(
  nwr["amenity"~"clinic|doctor"](area.inner)(area.outer);
);
out geom;
