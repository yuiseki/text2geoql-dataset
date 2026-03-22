[out:json][timeout:30];
area["name:en"="Montreal"]->.searchArea;
(
  nwr["amenity"="restaurant"](area.searchArea);
);
out geom;