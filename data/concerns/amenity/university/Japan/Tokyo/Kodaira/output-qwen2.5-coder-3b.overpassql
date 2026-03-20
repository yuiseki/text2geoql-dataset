[out:json][timeout:30];
area["name:en"="Kodaira"]->.outer;
(
  nwr["amenity"="university"](area.outer);
);
out geom;
