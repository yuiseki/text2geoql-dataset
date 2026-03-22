[out:json][timeout:30];
area["name:en"="Riyadh"]->.searchArea;
(
  nwr["amenity"="cafe"](area.searchArea);
);
out geom;