[out:json][timeout:30];
area["name:en"="Riyadh"]->.searchArea;
(
  nwr["amenity"="restaurant"](area.searchArea);
);
out geom;