[out:json][timeout:30];
area["name:en"="Budapest"]->.searchArea;
(
  nwr["amenity"="restaurant"](area.searchArea);
);
out geom;