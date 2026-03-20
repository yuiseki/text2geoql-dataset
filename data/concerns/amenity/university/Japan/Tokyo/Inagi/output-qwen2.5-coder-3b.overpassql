[out:json][timeout:30];
area["name:en"="Inagi"]->.outer;
(
  nwr["amenity"="university"](area.outer);
);
out geom;
