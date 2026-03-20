[out:json][timeout:30];
area["name:en"="Sham Shui Po District"]->.outer;
(
  nwr["amenity"~"bar"](area.outer);
);
out geom;
