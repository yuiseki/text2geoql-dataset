[out:json][timeout:30];
area["name:en"="Delhi"]->.searchArea;
(
  nwr["amenity"="restaurant"](area.searchArea);
);
out geom;