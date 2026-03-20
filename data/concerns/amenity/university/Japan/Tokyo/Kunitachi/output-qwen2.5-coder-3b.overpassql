[out:json][timeout:30];
area["name:en"="Kunitachi"]->.outer;
(
  nwr["amenity"="university"](area.outer);
);
out geom;
