[out:json][timeout:30];
area["name:en"="Sham Shui Po District"]->.outer;
(
  nwr["amenity"~"hospital"](area.outer);
);
out geom;
