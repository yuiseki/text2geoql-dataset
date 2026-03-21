[out:json][timeout:30];
area["name:en"="Sham Shui Po District"]->.outer;
(
  nwr["amenity"~"pharmacy"](area.outer);
);
out geom;
