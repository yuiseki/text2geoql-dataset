// Important note: SubArea: United States/New York
[out:json][timeout:30];
area["name:en"="New York"]["admin_level"=4]->.searchArea;
(
  relation["boundary"="administrative"]["admin_level"=6](area.searchArea);
);
out meta;
