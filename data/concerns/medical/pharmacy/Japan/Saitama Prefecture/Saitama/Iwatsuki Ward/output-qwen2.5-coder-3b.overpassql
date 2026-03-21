[out:json][timeout:30];
area["name:en"="Iwatsuki Ward"]->.outer;
area["name:en"="Saitama"]->.inner;
(
  nwr["amenity"~"pharmacy"](area.inner)(area.outer);
);
out geom;
