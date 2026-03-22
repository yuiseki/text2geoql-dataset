[out:json][timeout:30];
area["name:en"="Dublin"]->.searchArea;
(
  nwr["amenity"="restaurant"](area.searchArea);
);
out geom;