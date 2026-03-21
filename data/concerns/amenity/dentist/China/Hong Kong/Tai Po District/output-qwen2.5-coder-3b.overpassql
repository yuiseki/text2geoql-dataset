[out:json][timeout:30];
area["name:en"="Tai Po District"]->.outer;
(
  nwr["amenity"~"dentist"](area.outer);
);
out geom;
