[out:json][timeout:30];
area["name:en"="Pristina"]->.outer;
area["name:en"="Municipality of Pristina"]->.inner;
(
  nwr["amenity"~"dentist"](area.inner)(area.outer);
);
out geom;
