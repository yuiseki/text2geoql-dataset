[out:json][timeout:30];
area["name:en"="Wong Tai Sin District"]->.outer;
(
  nwr["amenity"~"dentist"](area.outer);
);
out geom;
