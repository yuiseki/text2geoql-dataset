[out:json][timeout:30];
area["name:en"="Sakura Ward"]->.outer;
area["name:en"="Saitama"]->.inner;
(
  nwr["amenity"~"clinic|doctor"](area.inner)(area.outer);
);
out geom;
