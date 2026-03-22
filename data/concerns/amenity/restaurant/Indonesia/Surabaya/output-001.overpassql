[out:json][timeout:30];
area["name:en"="Surabaya"]->.searchArea;
(
  nwr["amenity"="restaurant"](area.searchArea);
);
out geom;